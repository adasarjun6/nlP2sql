from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pymysql
import torch
from transformers import AutoTokenizer, AutoModel, T5ForConditionalGeneration

app = FastAPI()

origins = [
    "http://127.0.0.1:5500",  # Replace with your frontend's URL if different
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model loading
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

tokenizer_decoder = AutoTokenizer.from_pretrained("tscholak/2jrayxos")
model_decoder = T5ForConditionalGeneration.from_pretrained("tscholak/2jrayxos")


def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
    sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    return sum_embeddings / sum_mask


def encoder_decoder_1(query_sentence, table_names, tokenizer, model, cursor):
    query_sentence_encoded = tokenizer([query_sentence], padding=True, truncation=True, return_tensors="pt")
    table_names_encoded = tokenizer(table_names, padding=True, truncation=True, return_tensors="pt")

    with torch.no_grad():
        query_sentence_output = model(**query_sentence_encoded)
        table_names_output = model(**table_names_encoded)

    query_sentence_embeddings = mean_pooling(query_sentence_output, query_sentence_encoded["attention_mask"])
    table_names_embeddings = mean_pooling(table_names_output, table_names_encoded["attention_mask"])

    query_sentence_embeddings = torch.nn.functional.normalize(query_sentence_embeddings, p=2, dim=1)
    table_names_embeddings = torch.nn.functional.normalize(table_names_embeddings, p=2, dim=1)

    cosine_similarities_tables = torch.nn.functional.cosine_similarity(query_sentence_embeddings, table_names_embeddings, dim=1)
    most_similar_table_names_indeces = cosine_similarities_tables.argsort(descending=True)

    most_similar_table_names = [table_names[i] for i in most_similar_table_names_indeces]

    max_similaririty_table_index = cosine_similarities_tables.argmax()

    highest_matching_table_name = table_names[max_similaririty_table_index]

    cursor.execute(f"SHOW COLUMNS FROM {highest_matching_table_name};")
    highest_matching_table_names = [column_info[0] for column_info in cursor.fetchall()]

    highest_matching_table_column_names = ", ".join(highest_matching_table_names)
    highest_matching_table_column_names = list(highest_matching_table_column_names.split(", "))
    highest_matching_table_column_names = [column_name.replace(' ', '_') for column_name in highest_matching_table_column_names]

    return highest_matching_table_name, highest_matching_table_column_names


def encoder_decoder_2(query_sentence, database_name, highest_matching_table_name, highest_matching_table_column_names, tokenizer_decoder, model_decoder):
    input_text = query_sentence + " | " + highest_matching_table_name + " | " + str(highest_matching_table_column_names)

    input_ids = tokenizer_decoder.encode(input_text, return_tensors="pt")

    output = model_decoder.generate(input_ids, max_length=128, num_beams=4, early_stopping=True)

    output_text = tokenizer_decoder.decode(output[0], skip_special_tokens=True)

    # Removing unwanted parts from the output
    if " | " in output_text:
        sql_query = output_text.split(" | ")[-1].strip()
    else:
        sql_query = output_text.strip()

    # Fix the formatting issues
    sql_query = sql_query.replace(" ( ", "(").replace(" ) ", ")")

    return sql_query


def sql_executor(sql_query, highest_matching_table_column_names, cursor):
    highest_matching_table_column_names = [x.lower() for x in highest_matching_table_column_names]

    for i in highest_matching_table_column_names:
        if i in sql_query:
            sql_query = sql_query.replace(i, ''+i+'')

    sql_query = sql_query.replace("_", " ")
    sql_query = sql_query.replace("'", '"')

    cursor.execute(sql_query)
    results = cursor.fetchall()
    return results


class QueryRequest(BaseModel):
    query_sentence: str


@app.post("/execute_query")
def execute_query(request: QueryRequest):
    query_sentence = request.query_sentence

    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="manash2009",
        database="apt_db"
    )
    cursor = conn.cursor()

    cursor.execute("SELECT DATABASE();")
    database_name = cursor.fetchone()[0]

    cursor.execute("SHOW TABLES;")
    table_names = [table_info[0] for table_info in cursor.fetchall()]

    highest_matching_table_name, highest_matching_table_column_names = encoder_decoder_1(query_sentence, table_names, tokenizer, model, cursor)

    sql_query = encoder_decoder_2(query_sentence, database_name, highest_matching_table_name, highest_matching_table_column_names, tokenizer_decoder, model_decoder)

    results = sql_executor(sql_query, highest_matching_table_column_names, cursor)

    conn.close()

    return {"query": sql_query, "results": results}