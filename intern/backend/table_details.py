import pandas as pd
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Load your custom NL2SQL model and tokenizer
model_name = "charanhu/text_to_sql_5"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def get_table_details():
    csv_file = 'database_table_descriptions.csv'
    
    # Read the CSV file into a DataFrame
    table_description = pd.read_csv(csv_file)
    
    table_details = ""
    
    # Iterate over the DataFrame rows to create table details
    for index, row in table_description.iterrows():
        table_details += f"Table Name: {row['Table']}\nTable Description: {row['Description']}\n\n"
    
    return table_details

# Function to generate SQL queries using your custom NL2SQL model
def generate_sql_query(question, table_details):
    input_text = f"question: {question} context: {table_details}"
    inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(inputs, max_length=100)
    sql_query = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return sql_query

# Function to answer questions using your custom NL2SQL model
def answer_question(question, sql_result):
    input_text = f"question: {question} context: {sql_result}"
    inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(inputs, max_length=100)
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return answer

# For testing purposes
if __name__ == "__main__":
    table_details = get_table_details()
    print(table_details)
    
    question = "What are the details of the project with ID 5?"
    sql_query = generate_sql_query(question, table_details)
    print(f"Generated SQL Query: {sql_query}")
