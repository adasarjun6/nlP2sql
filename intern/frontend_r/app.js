// used for charanhu
document
  .getElementById("message_area")
  .addEventListener("submit", async function (event) {
    event.preventDefault(); // Prevent the default form submission

    const chatInput = document.getElementById("text");
    const chatHistory = document.getElementById("chatHistory");
    const userMessage = chatInput.value.trim();

    if (userMessage === "") {
      return;
    }

    // Display the user's message in the chat history
    const userMessageDiv = document.createElement("div");
    userMessageDiv.classList.add("response_tab_user", "user");
    userMessageDiv.textContent = userMessage;
    chatHistory.appendChild(userMessageDiv);

    // Clear the input field
    chatInput.value = "";

    try {
      // Send the user's message to the FastAPI backend
      const response = await fetch("https://7776-34-83-9-36.ngrok-free.app/generate_sql/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: userMessage }),
      });

      if (response.ok) {
        const data = await response.json();
        const sqlQuery = data.sql_query;
        const results = data.results;

        // Display the generated SQL query in the chat history
        const sqlQueryDiv = document.createElement("div");
        sqlQueryDiv.classList.add("response_tab_assistant", "assistant");
        sqlQueryDiv.textContent = "Generated SQL Query: " + sqlQuery;
        chatHistory.appendChild(sqlQueryDiv);

        // Display the SQL query results in the chat history
        if (results.length > 0) {
          const resultsDiv = document.createElement("div");
          resultsDiv.classList.add("response_tab_assistant", "assistant");

          const table = document.createElement("table");
          const thead = document.createElement("thead");
          const tbody = document.createElement("tbody");

          // Set table headers
          const headers = Object.keys(results[0]);
          const headerRow = document.createElement("tr");
          headers.forEach((header) => {
            const th = document.createElement("th");
            th.innerText = header;
            headerRow.appendChild(th);
          });
          thead.appendChild(headerRow);

          // Set table rows
          results.forEach((row) => {
            const tr = document.createElement("tr");
            headers.forEach((header) => {
              const td = document.createElement("td");
              td.innerText = row[header];
              tr.appendChild(td);
            });
            tbody.appendChild(tr);
          });

          table.appendChild(thead);
          table.appendChild(tbody);
          resultsDiv.appendChild(table);
          chatHistory.appendChild(resultsDiv);
        } else {
          const noResultsDiv = document.createElement("div");
          noResultsDiv.classList.add("response_tab_assistant", "assistant");
          noResultsDiv.textContent = "No results found.";
          chatHistory.appendChild(noResultsDiv);
        }

        // Scroll to the bottom of the chat history
        chatHistory.scrollTop = chatHistory.scrollHeight;
      } else {
        console.error("Failed to send message to the backend");
      }
    } catch (error) {
      console.error("Error:", error);
    }
  });

// // document.getElementById("message_area").addEventListener("submit", async function (event) {
// //     event.preventDefault(); // Prevent the default form submission

// //     const chatInput = document.getElementById("text");
// //     const chatHistory = document.getElementById("chatHistory");
// //     const userMessage = chatInput.value.trim();

// //     if (userMessage === "") {
// //         return;
// //     }

// //     // Display the user's message in the chat history
// //     const userMessageDiv = document.createElement("div");
// //     userMessageDiv.classList.add("response_tab_user", "user");
// //     userMessageDiv.textContent = userMessage;
// //     chatHistory.appendChild(userMessageDiv);

// //     // Clear the input field
// //     chatInput.value = "";

// //     try {
// //         // Send the user's message to the FastAPI backend
// //         const response = await fetch("http://127.0.0.1:8000/generate_sql/", {
// //             method: "POST",
// //             headers: {
// //                 "Content-Type": "application/json",
// //             },
// //             body: JSON.stringify({ question: userMessage }),
// //         });

// //         if (response.ok) {
// //             const data = await response.json();
// //             const assistantMessage = data.query;
// //             const queryResults = data.results;

// //             // Display the assistant's generated SQL query in the chat history
// //             const assistantMessageDiv = document.createElement("div");
// //             assistantMessageDiv.classList.add("response_tab_assistant", "assistant");
// //             assistantMessageDiv.textContent = assistantMessage;
// //             chatHistory.appendChild(assistantMessageDiv);

// //             // Create a table to display the query results
// //             if (queryResults && queryResults.columns && queryResults.rows) {
// //                 const table = document.createElement("table");
// //                 const thead = document.createElement("thead");
// //                 const tbody = document.createElement("tbody");

// //                 // Create table header
// //                 const headerRow = document.createElement("tr");
// //                 queryResults.columns.forEach((column) => {
// //                     const th = document.createElement("th");
// //                     th.textContent = column;
// //                     headerRow.appendChild(th);
// //                 });
// //                 thead.appendChild(headerRow);

// //                 // Create table body
// //                 queryResults.rows.forEach((row) => {
// //                     const tr = document.createElement("tr");
// //                     row.forEach((cell) => {
// //                         const td = document.createElement("td");
// //                         td.textContent = cell;
// //                         tr.appendChild(td);
// //                     });
// //                     tbody.appendChild(tr);
// //                 });

// //                 table.appendChild(thead);
// //                 table.appendChild(tbody);
// //                 chatHistory.appendChild(table);
// //             }

// //             // Scroll to the bottom of the chat history
// //             chatHistory.scrollTop = chatHistory.scrollHeight;
// //         } else {
// //             console.error("Failed to send message to the backend");
// //         }
// //     } catch (error) {
// //         console.error("Error:", error);
// //     }
// // });

// document.getElementById("message_area").addEventListener("submit", async function (event) {
//     event.preventDefault(); // Prevent the default form submission

//     const chatInput = document.getElementById("text");
//     const chatHistory = document.getElementById("chatHistory");
//     const userMessage = chatInput.value.trim();

//     if (userMessage === "") {
//         return;
//     }

//     // Display the user's message in the chat history
//     const userMessageDiv = document.createElement("div");
//     userMessageDiv.classList.add("response_tab_user", "user");
//     userMessageDiv.textContent = userMessage;
//     chatHistory.appendChild(userMessageDiv);

//     // Clear the input field
//     chatInput.value = "";

//     try {
//         // Send the user's message to the FastAPI backend
//         const response = await fetch("http://127.0.0.1:8000/generate_sql/", {
//             method: "POST",
//             headers: {
//                 "Content-Type": "application/json",
//             },
//             body: JSON.stringify({ question: userMessage }),
//         });

//         if (response.ok) {
//             const data = await response.json();
//             const assistantMessage = data.query;
//             const queryResults = data.results;

//             // Display the assistant's generated SQL query in the chat history
//             const assistantMessageDiv = document.createElement("div");
//             assistantMessageDiv.classList.add("response_tab_assistant", "assistant");
//             assistantMessageDiv.textContent = assistantMessage+queryResults;
//             chatHistory.appendChild(assistantMessageDiv);

//             // Create a table to display the query results
//             if (queryResults && queryResults.columns && queryResults.rows) {
//                 const table = document.createElement("table");
//                 const thead = document.createElement("thead");
//                 const tbody = document.createElement("tbody");

//                 // Create table header
//                 const headerRow = document.createElement("tr");
//                 queryResults.columns.forEach((column) => {
//                     const th = document.createElement("th");
//                     th.textContent = column;
//                     headerRow.appendChild(th);
//                 });
//                 thead.appendChild(headerRow);

//                 // Create table body
//                 queryResults.rows.forEach((row) => {
//                     const tr = document.createElement("tr");
//                     row.forEach((cell) => {
//                         const td = document.createElement("td");
//                         td.textContent = cell;
//                         tr.appendChild(td);
//                     });
//                     tbody.appendChild(tr);
//                 });

//                 table.appendChild(thead);
//                 table.appendChild(tbody);
//                 chatHistory.appendChild(table);
//             }

//             // Scroll to the bottom of the chat history
//             chatHistory.scrollTop = chatHistory.scrollHeight;
//         } else {
//             console.error("Failed to send message to the backend");
//         }
//     } catch (error) {
//         console.error("Error:", error);
//     }
// });