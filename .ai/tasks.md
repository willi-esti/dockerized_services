# Tasks and Todos

## Phase 1: Data Pipeline (Kronos)

**Goal:** Implement a robust data pipeline that automatically exports data from Planka, processes it, and stores it in a PostgreSQL database with the `pgvector` extension.

**Status:** In Progress

### Done

*   Docker Compose environment is set up.
*   Dockerfiles for all services are created.
*   Initial data export script from Planka is implemented (`services/background_task.py`).
*   Standalone data processing script is created (`main1.py`), which includes file loading, chunking, embedding, and database storage.

### To Do

1.  **Enable `pgvector` extension:** Ensure the `pgvector` extension is enabled in the PostgreSQL container. This may require modifying the `docker/postgres/Dockerfile` or the `db/init.sql` script.
2.  **Integrate data pipeline:** Merge the logic from `main1.py` into the `services/background_task.py` script. This will involve:
    *   Reading the exported card data from the text files.
    *   Chunking the text content.
    *   Generating vector embeddings.
    *   Storing the chunks and embeddings in the database.
3.  **Enable continuous synchronization:** Uncomment the `while` loop in the `sync_databases()` function to ensure that the data is continuously updated.
4.  **Add error handling and logging:** Implement robust error handling and logging to ensure the data pipeline is reliable.

## Phase 2: Backend API (Kronos)

**Goal:** Create a FastAPI application that provides an API for searching the vectorized data.

**Status:** Not Started

### To Do

1.  **Create a search endpoint:** Implement a new API endpoint (e.g., `/search`) that accepts a query string.
2.  **Implement vector search:** In the search endpoint, perform the following steps:
    *   Generate a vector embedding for the query string.
    *   Use the `pgvector` extension to perform a similarity search on the stored vectors.
    *   Return the most relevant cards and their content.
3.  **Implement a chat endpoint:** Create a new API endpoint (e.g., `/chat`) that accepts a user's question and returns a natural language response. This will involve:
    *   Using the search endpoint to find relevant cards.
    *   Passing the relevant cards and the user's question to a large language model (LLM).
    *   Returning the LLM's response to the user.

## Phase 3: Web UI

**Goal:** Create a user-friendly web interface for interacting with the AI.

**Status:** Not Started

### To Do

1.  **Choose a frontend framework:** Select a frontend framework for the web UI (e.g., React, Vue, or Svelte).
2.  **Design the UI:** Create a simple and intuitive UI with a search bar and a chat window.
3.  **Implement the UI:** Develop the frontend application and connect it to the backend API.
