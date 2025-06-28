# Project Knowledge

## Project Goal

The primary goal of this project is to export data from a Planka instance, process it, and store it in a vector database. This will enable an AI to perform semantic search and other tasks on the Planka data.

## High-Level Architecture

The system is composed of two main parts:

1.  **FastAPI Application:** A Python-based web application that provides an API for interacting with the vectorized data. It also includes a background task that continuously synchronizes data from Planka.
2.  **Data Ingestion Pipeline:** A set of scripts that perform the following steps:
    *   Export data from the Planka database.
    *   Split the data into smaller chunks.
    *   Generate vector embeddings for each chunk using a pre-trained model.
    *   Store the chunks and their embeddings in a PostgreSQL database.

## Data Pipeline

The data pipeline is implemented in the `kronos/src/ingest` directory and consists of the following steps:

1.  **Data Loading:** The `loader.py` script recursively finds all files with supported extensions (`.txt`, `.md`, `.pdf`, `.json`, `.csv`) in a given directory.
2.  **Chunking:** The `chunker.py` script takes a file path, reads the text content, and splits it into overlapping chunks of a specified size. It uses a tokenizer from the `transformers` library to ensure that the chunks are of a consistent length in terms of tokens.
3.  **Embedding:** The `embedder.py` script takes a list of text chunks and uses a pre-trained model from the `sentence-transformers` library to convert them into vector embeddings.
4.  **Storage:** The `main1.py` script provides a clear example of how to store the chunks and their embeddings in the database. It uses the `db_config.py` script to interact with the PostgreSQL database. The chosen vector store is **PostgreSQL with the `pgvector` extension**.

## Code Structure

The project is organized into the following key directories:

*   `kronos/src`: The main application directory.
    *   `ingest`: Contains the data ingestion pipeline scripts.
    *   `routes`: Defines the API endpoints for the FastAPI application.
    *   `services`: Contains the business logic for the application, including the background task for data synchronization.
    *   `utils`: Contains utility functions for logging, database interaction, and environment variable management.
*   `docker`: Contains the Dockerfiles for building the application and its dependencies.
*   `data`: The default directory for storing the exported Planka data.

## Key Functions

*   `sync_databases()` in `services/background_task.py`: The main entry point for the data synchronization process.
*   `export_updated_cards()` in `services/background_task.py`: Exports all cards that have been updated after a specified date from the Planka database.
*   `smart_overlap_chunk()` in `ingest/chunker.py`: Splits a text file into overlapping chunks of a specified size.
*   `embed_chunks()` in `ingest/embedder.py`: Converts a list of text chunks into vector embeddings.
*   `insert_knowledge_item()`, `insert_source_file()`, and `insert_chunk()` in `utils/db_config.py`: Functions for storing the data in the PostgreSQL database.

## Next Steps

1.  **Uncomment the `while` loop** in `sync_databases()` to enable continuous synchronization.
2.  **Integrate the chunking and embedding logic** from `main1.py` into the `export_single_card()` function in `services/background_task.py`.
3.  **Add a function to store the embeddings** in the vector database, using the `db_config.py` script as a reference.
4.  **Implement the API endpoints** in the `routes` directory to provide access to the vectorized data.
