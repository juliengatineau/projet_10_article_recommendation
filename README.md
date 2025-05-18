# Article Recommendation System (Azure Function App)

This project implements a **serverless recommendation system** using **Azure Functions** and **Azure Blob Storage**. It returns personalized article recommendations for a given user based on previously viewed articles and a similarity model computed with **FAISS**.

## Description

The system uses the following components:

- **Local Interface** (HTTP-triggered Azure Function)
- **Azure Blob Storage** (stores precomputed data)
- **Azure Function App** (executes the recommendation logic)

## Recommendation Logic

1. For each article read by a user, retrieve the top 10 similar articles (using a FAISS-based similarity dictionary).
2. Aggregate all the similar articles across the user’s reading history.
3. Recommend the articles that are most frequently suggested.
4. If not enough high-frequency candidates are found, fallback to recommendations from the **last read article**.

## Technologies Used

- Python 3.8+
- Azure Functions (v4)
- Azure Blob Storage
- Pandas – Data manipulation
- NumPy – Numerical operations
- Pickle – For loading precomputed similarity data
- FAISS – (offline) Similarity search to generate article embeddings
- Logging – For tracking and debugging errors
