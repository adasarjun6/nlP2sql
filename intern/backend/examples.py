import torch
import streamlit as st
from transformers import AutoTokenizer, AutoModel
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_community.vectorstores import Chroma

# Load custom tokenizer and model
tokenizer = AutoTokenizer.from_pretrained('charanhu/text_to_sql_5')
custom_model = AutoModel.from_pretrained('charanhu/text_to_sql_5')

@st.cache_data
def get_custom_embeddings(text):
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        outputs = custom_model(**inputs)
        embeddings = torch.mean(outputs.last_hidden_state, dim=1)  # Mean pooling over tokens
    return embeddings.numpy()

@st.cache_resource
def get_example_selector():
    vector_store = Chroma()
    example_embeddings = []
    examples = [
        {
        "input": "Find me the most used email address",
        "query": "SELECT Email, COUNT(*) AS Count FROM employees GROUP BY Email ORDER BY Count DESC LIMIT 1"
    },
    {
        "input": "Show the average salary for employees in each department.",
        "query": "SELECT Department, AVG(Salary) AS AverageSalary FROM employees GROUP BY Department"
    },
    {
        "input": "Find clients in a specific state or postal code range, excluding a particular client.",
        "query": "SELECT c.ClientName, c.State, c.PostalCode FROM clients c WHERE c.State = \"CA\" OR (c.PostalCode >= \"94101\" AND c.PostalCode <= \"94199\") AND c.ClientID != 2"
    },
    {
        "input": "Clients Who Spent Over $100,000",
        "query": "SELECT c.ClientName, SUM(p.Budget) AS TotalSpent FROM clients c JOIN projects p ON c.ClientID = p.ClientID GROUP BY c.ClientID HAVING SUM(p.Budget) > 100000 ORDER BY TotalSpent DESC LIMIT 5"
    },
    {
        "input": "Average Services Ordered by Clients in New York",
        "query": "SELECT AVG(s.Price) AS AvgPrice FROM projects AS p JOIN clients AS c ON p.ClientID = c.ClientID JOIN projectassignments AS pa ON p.ProjectID = pa.ProjectID JOIN employees AS e ON pa.EmployeeID = e.EmployeeID JOIN services AS s ON p.ProjectName = s.ServiceName WHERE c.City = \"New York\" GROUP BY p.ClientID"
    },
    {
        "input": "Clients Who Spent More Than the Average Service Price Across All Clients",
        "query": "SELECT c.ClientName, SUM(p.Budget) AS TotalSpent FROM projects p JOIN clients c ON p.ClientID = c.ClientID GROUP BY c.ClientID HAVING SUM(p.Budget) > (SELECT AVG(s.Price) FROM services s) ORDER BY TotalSpent DESC LIMIT 5"
    },
    {
        "input": "Which project is most time consuming?",
        "query": "SELECT ProjectName, TIMESTAMPDIFF(DAY, StartDate, EndDate) AS Duration FROM projects ORDER BY Duration DESC LIMIT 1"
    },
    {
        "input": "Find me which projects client more invested in",
        "query": "SELECT t1.ProjectName, t1.Budget, t2.ClientName FROM projects AS t1 INNER JOIN clients AS t2 ON t1.ClientID = t2.ClientID ORDER BY t1.Budget DESC LIMIT 5"
    },
    {
        "input": "Which employees currently do not have any ongoing projects assigned to them?",
        "query": "SELECT DISTINCT e.EmployeeID, e.FirstName, e.LastName FROM Employees e LEFT JOIN ProjectAssignments pa ON e.EmployeeID = pa.EmployeeID LEFT JOIN Projects p ON pa.ProjectID = p.ProjectID AND p.Status = \"Ongoing\" WHERE p.ProjectID IS NULL;"
    },
    {
        "input": "Which project is not started yet",
        "query": "SELECT ProjectName FROM projects WHERE StartDate > CURDATE()"
    },
    {
        "input": "How many employees are currently assigned to each ongoing project, and what is the total budget allocated for these projects?",
        "query": "SELECT p.ProjectName, COUNT(pa.EmployeeID), SUM(p.Budget) FROM projects p JOIN projectassignments pa ON p.ProjectID = pa.ProjectID WHERE p.Status = \"Ongoing\" GROUP BY p.ProjectName"
    },
    {
        "input": "For each client, how many projects have been completed, ongoing, or are yet to start, and what is the total budget allocated to each category?",
        "query": "SELECT c.ClientName, COUNT(CASE WHEN p.Status = \"Completed\" THEN 1 END) AS CompletedProjects, COUNT(CASE WHEN p.Status = \"Ongoing\" THEN 1 END) AS OngoingProjects, COUNT(CASE WHEN p.Status = \"Yet to start\" THEN 1 END) AS YetToStartProjects, SUM(p.Budget) AS TotalBudget FROM clients c JOIN projects p ON c.ClientID = p.ClientID GROUP BY c.ClientID ORDER BY c.ClientName"
    },
    {
        "input": "Retrieve clients who have projects both ongoing and completed",
        "query": "SELECT DISTINCT c.ClientID, c.ClientName FROM Clients c JOIN Projects p ON c.ClientID = p.ClientID WHERE EXISTS ( SELECT 1 FROM Projects p2 WHERE p2.ClientID = c.ClientID AND p2.Status = \"Ongoing\" ) AND EXISTS ( SELECT 1 FROM Projects p3 WHERE p3.ClientID = c.ClientID AND p3.Status = \"Completed\" );"
    },
    {
        "input": "List all employees who are assigned to every project",
        "query": "SELECT e.EmployeeID, e.FirstName, e.LastName FROM Employees e WHERE NOT EXISTS ( SELECT p.ProjectID FROM Projects p WHERE NOT EXISTS ( SELECT pa2.EmployeeID FROM ProjectAssignments pa2 WHERE pa2.EmployeeID = e.EmployeeID AND pa2.ProjectID = p.ProjectID ));"
    },
    {
        "input": "Which employees have roles assigned across all projects, and what are their names?",
        "query": "SELECT e.EmployeeID, e.FirstName, e.LastName FROM Employees e WHERE NOT EXISTS ( SELECT p.ProjectID FROM Projects p WHERE NOT EXISTS ( SELECT pa2.EmployeeID FROM ProjectAssignments pa2 WHERE pa2.EmployeeID = e.EmployeeID AND pa2.ProjectID = p.ProjectID ));"
    },
    {
        "input": "Retrieve clients who have ongoing projects but no completed projects.",
        "query": "SELECT DISTINCT c.ClientName FROM Clients c JOIN Projects p ON c.ClientID = p.ClientID WHERE p.Status = \"Ongoing\" AND NOT EXISTS ( SELECT 1 FROM Projects p2 WHERE p2.ClientID = c.ClientID AND p2.Status = \"Completed\" );"
    },
    {
        "input": "Which employees have been assigned roles across all projects, and what roles do they hold?",
        "query": "SELECT e.EmployeeID, e.FirstName, e.LastName, pa.Role FROM Employees e JOIN ProjectAssignments pa ON e.EmployeeID = pa.EmployeeID WHERE NOT EXISTS ( SELECT p.ProjectID FROM Projects p WHERE NOT EXISTS ( SELECT 1 FROM ProjectAssignments pa2 WHERE pa2.EmployeeID = e.EmployeeID AND pa2.ProjectID = p.ProjectID ));"
    },
    {
        "input": "Find employees who have been assigned to all projects and their roles.",
        "query": "SELECT e.EmployeeID, e.FirstName, e.LastName, pa.Role FROM Employees e JOIN ProjectAssignments pa ON e.EmployeeID = pa.EmployeeID WHERE NOT EXISTS ( SELECT p.ProjectID FROM Projects p WHERE NOT EXISTS ( SELECT 1 FROM ProjectAssignments pa2 WHERE pa2.EmployeeID = e.EmployeeID AND pa2.ProjectID = p.ProjectID ));"
    },
    {
        "input": "Find clients who have projects with a budget exceeding the average budget of all projects.",
        "query": "SELECT c.ClientName FROM Clients c WHERE EXISTS ( SELECT 1 FROM Projects p WHERE p.ClientID = c.ClientID AND p.Budget > ( SELECT AVG(p2.Budget) FROM Projects p2 ));"
    },
    {
        "input": "Find all clients who do not have any associated projects.",
        "query": "SELECT c.ClientName FROM Clients c LEFT JOIN Projects p ON c.ClientID = p.ClientID WHERE p.ProjectID IS NULL;"
    },
    {
        "input": "Clients with Most Ongoing Projects.",
        "query": "SELECT c.ClientName, COUNT(p.ProjectID) AS NumOfProjects FROM Clients c JOIN Projects p ON c.ClientID = p.ClientID WHERE p.Status = \"Ongoing\" GROUP BY c.ClientName ORDER BY NumOfProjects DESC LIMIT 5"
    },
    {
        "input": "Identify the employee who has worked on the highest number of projects and list those projects.",
        "query": "SELECT e.FirstName, e.LastName, COUNT(pa.ProjectID) AS NumOfProjects FROM Employees e JOIN ProjectAssignments pa ON e.EmployeeID = pa.EmployeeID GROUP BY e.EmployeeID ORDER BY NumOfProjects DESC LIMIT 1"
    },
    {
        "input": "Find the total number of projects currently assigned to each employee, including their full name and department. List the employees starting from those assigned to the most projects to those with the least.",
        "query": "SELECT e.FirstName, e.LastName, d.Department, COUNT(pa.ProjectID) AS NumOfProjects FROM Employees e JOIN ProjectAssignments pa ON e.EmployeeID = pa.EmployeeID JOIN Departments d ON e.DepartmentID = d.DepartmentID GROUP BY e.EmployeeID ORDER BY NumOfProjects DESC"
    },
    {
        "input": "List all employees who have not been assigned to any projects yet, along with their departments.",
        "query": "SELECT e.FirstName, e.LastName, d.Department FROM Employees e JOIN Departments d ON e.DepartmentID = d.DepartmentID WHERE e.EmployeeID NOT IN ( SELECT DISTINCT EmployeeID FROM ProjectAssignments );"
    },
    {
        "input": "Find all employees who have worked on more than one project. For each of these employees, list their total number of projects, the total budget allocated to those projects, and the average salary of employees who have worked on those projects. Include only employees whose average salary is above the company-wide average salary.",
        "query": "SELECT e.EmployeeID, e.FirstName, e.LastName, COUNT(pa.ProjectID) AS NumOfProjects, SUM(p.Budget) AS TotalBudget, AVG(e.Salary) AS AvgSalary FROM Employees e JOIN ProjectAssignments pa ON e.EmployeeID = pa.EmployeeID JOIN Projects p ON pa.ProjectID = p.ProjectID GROUP BY e.EmployeeID HAVING COUNT(pa.ProjectID) > 1 AND AVG(e.Salary) > ( SELECT AVG(Salary) FROM Employees );"
    },
    {
        "input": "Find the employees who have worked on projects for multiple clients and list their names along with the number of distinct clients they have worked for.",
        "query": "SELECT e.EmployeeID, e.FirstName, e.LastName, COUNT(DISTINCT p.ClientID) AS NumOfClients FROM Employees e JOIN ProjectAssignments pa ON e.EmployeeID = pa.EmployeeID JOIN Projects p ON pa.ProjectID = p.ProjectID GROUP BY e.EmployeeID HAVING COUNT(DISTINCT p.ClientID) > 1;"
    },
    {
        "input": "Find the average salary and name of employees who are assigned to projects with a budget greater than the overall average budget of all projects.",
        "query": "SELECT e.FirstName, e.LastName, AVG(e.Salary) AS AvgSalary FROM Employees e JOIN ProjectAssignments pa ON e.EmployeeID = pa.EmployeeID JOIN Projects p ON pa.ProjectID = p.ProjectID WHERE p.Budget > ( SELECT AVG(Budget) FROM Projects ) GROUP BY e.EmployeeID;"
    },
    {
        "input": "Find all employees who are involved in more than one project and whose average salary is higher than the overall average salary of all employees. For each such employee, include their ID, first name, last name, the number of distinct projects they are assigned to, the total budget of these projects, and their average salary. Sort the results by average salary in descending order.",
        "query": "SELECT e.EmployeeID, e.FirstName, e.LastName, COUNT(DISTINCT pa.ProjectID) AS NumOfProjects, SUM(p.Budget) AS TotalBudget, AVG(e.Salary) AS AvgSalary FROM Employees e JOIN ProjectAssignments pa ON e.EmployeeID = pa.EmployeeID JOIN Projects p ON pa.ProjectID = p.ProjectID GROUP BY e.EmployeeID HAVING COUNT(DISTINCT pa.ProjectID) > 1 AND AVG(e.Salary) > ( SELECT AVG(Salary) FROM Employees ) ORDER BY AvgSalary DESC;"
    },
    {
        "input": "List clients who have more than one ongoing project. Include the client's name, contact person, email, and the number of ongoing projects.",
        "query": "SELECT c.ClientName, c.ContactPerson, c.Email, COUNT(p.ProjectID) AS NumOfOngoingProjects FROM Clients c JOIN Projects p ON c.ClientID = p.ClientID WHERE p.Status = \"Ongoing\" GROUP BY c.ClientID HAVING COUNT(p.ProjectID) > 1;"
    },
    {
        "input": "Find the projects with the highest number of employees assigned. Include the project name, client name, and the number of employees assigned.",
        "query": "SELECT p.ProjectName, c.ClientName, COUNT(pa.EmployeeID) AS NumOfEmployees FROM Projects p JOIN Clients c ON p.ClientID = c.ClientID JOIN ProjectAssignments pa ON p.ProjectID = pa.ProjectID GROUP BY p.ProjectID ORDER BY NumOfEmployees DESC LIMIT 1;"
    },
    {
        "input": "List all engineers with a salary over $60,000.",
        "query": "SELECT e.FirstName, e.LastName FROM Employees e JOIN Departments d ON e.DepartmentID = d.DepartmentID WHERE d.DepartmentName = \"Engineering\" AND e.Salary > 60000;"
    },
    {
        "input": "Show project details for projects in the 'Machine' category.",
        "query": "SELECT * FROM Projects WHERE Category = \"Machine\";"
    },
    {
        "input": "List all clients in New York.",
        "query": "SELECT * FROM Clients WHERE City = \"New York\";"
    },
    {
        "input": "Find the total budget allocated for all ongoing projects.",
        "query": "SELECT SUM(Budget) AS TotalBudget FROM Projects WHERE Status = \"Ongoing\";"
    },
    {
        "input": "Show all projects with a budget exceeding $100,000.",
        "query": "SELECT * FROM Projects WHERE Budget > 100000;"
    },
    {
        "input": "List all employees with a salary exceeding $90,000.",
        "query": "SELECT * FROM Employees WHERE Salary > 90000;"
    }
    ]

    for example in examples:
        embedding = get_custom_embeddings(example["input"])
        vector_store.add_item(embedding, example)
        example_embeddings.append(embedding)

    example_selector = SemanticSimilarityExampleSelector(
        vectorstore=vector_store,
        k=2,
        input_keys=["input"],
    )
    return example_selector

# Streamlit application code can follow here
if __name__ == "__main__":
    st.title("Custom NL2SQL Example Selector")
    example_selector = get_example_selector()

    user_input = st.text_input("Enter your query:")
    if user_input:
        embedding = get_custom_embeddings(user_input)
        selected_examples = example_selector.select_examples(embedding)
        st.write("Selected Examples:")
        for example in selected_examples:
            st.write(f"Input: {example['input']}")
            st.write(f"Query: {example['query']}")
