from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate, PromptTemplate
from examples import get_example_selector  # Ensure this is correctly defined

# Example selector initialization
example_selector = get_example_selector()  # Ensure this is correctly defined

# Define a ChatPromptTemplate for user input and SQL query generation
user_input_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}\nSQLQuery:"),
        ("ai", "{query}"),
    ]
)

# Define a FewShotChatMessagePromptTemplate for handling example selection and input variables
few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=user_input_prompt,
    example_selector=example_selector,  # Correctly pass the example selector
    input_variables=["input", "top_k"],  # Adjust input variables as per your requirements
)

# Define a ChatPromptTemplate for final user interaction
final_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a MySQL expert. Given an input question, create a syntactically correct MySQL query to run."),
        few_shot_prompt,
        ("human", "{input}"),
    ]
)

# Define a PromptTemplate for answering questions based on SQL queries
answer_template = PromptTemplate.from_template(
    """
    Given the following user question and corresponding SQL query, answer the user question.

    Question: {question}
    SQL Query: {query}
    Answer: {answer}
    """
)
