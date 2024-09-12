import chromadb
from chromadb.utils import embedding_functions
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from fastapi import FastAPI, HTTPException
import os
import requests
import pandas as pd
import io
import logging
import traceback

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()
os.environ['HF_HUB_DOWNLOAD_TIMEOUT'] = '500'

CHROMA_DB_PATH = './'
#CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "/app/data/chroma")
HF_HOME = os.getenv("HF_HOME", "/root/.cache/huggingface")

logger.info(f"Initializing Chroma client with path: {CHROMA_DB_PATH}")
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
logger.info("Chroma client initialized successfully")

logger.info("Initializing embedding function")
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="WpythonW/RUbert-tiny_custom_test_2",
)
logger.info("Embedding function initialized successfully")

EMBEDDING_DIMENSION = len(emb_fn("test"))
logger.info(f"Embedding dimension: {EMBEDDING_DIMENSION}")

def get_or_create_collection(name="qa_corpus"):
    logger.info(f"Getting or creating collection: {name}")
    try:
        collection = chroma_client.get_collection(name=name, embedding_function=emb_fn)
        logger.info(f"Collection '{name}' retrieved successfully")
        return collection
    except ValueError:
        logger.info(f"Collection '{name}' not found, creating new collection")
        collection = chroma_client.create_collection(
            name=name,
            embedding_function=emb_fn,
            metadata={"hnsw:space": "cosine", "dimension": EMBEDDING_DIMENSION}
        )
        logger.info(f"Collection '{name}' created successfully")
        return collection

default_collection = get_or_create_collection()

class Query(BaseModel):
    queries: List[str]
    n_results: int = 3

class GoogleSheetInfo(BaseModel):
    sheet_id: str
    gid: str
    collection: Optional[str] = None

class BatchAddition(BaseModel):
    questions: List[str]
    answers: List[str]
    collection: Optional[str] = None

@app.post("/api/v1/get_answer/")
async def query(query_data: Query):
    logger.info(f"Received query: {query_data}")
    try:
        results = default_collection.query(
            query_texts=query_data.queries,
            n_results=query_data.n_results,
            include=['metadatas', 'documents', 'distances']
        )
        
        formatted_results = []
        for i, query in enumerate(query_data.queries):
            query_results = []
            for j in range(len(results['ids'][i])):
                result = {
                    "id": results['ids'][i][j],
                    "question": results['documents'][i][j] if results['documents'] else "No question available",
                    "answer": results['metadatas'][i][j].get("answer", "No answer available") if results['metadatas'] else "No answer available",
                    "distance": results['distances'][i][j] if results['distances'] else None
                }
                query_results.append(result)
            
            formatted_results.append({
                "query": query,
                "results": query_results
            })
        
        logger.info(f"Query results: {formatted_results}")
        return {"results": formatted_results}
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

def batch_addition(questions, answers, collection_name=None):
    logger.info(f"Adding batch of {len(questions)} questions to collection: {collection_name or 'default'}")
    collection = get_or_create_collection(collection_name) if collection_name else default_collection
    
    existing_docs = collection.get(include=['documents'])
    existing_questions = set(existing_docs['documents'])
    
    unique_questions = {}
    questions_to_add = []
    answers_to_add = []
    
    for question, answer in zip(questions, answers):
        if question not in existing_questions and question not in unique_questions:
            questions_to_add.append(question)
            answers_to_add.append({"answer": answer})
            unique_questions[question] = True
    
    if questions_to_add:
        new_ids = [str(i) for i in range(len(existing_questions), len(existing_questions) + len(questions_to_add))]
        logger.info(f"Adding {len(questions_to_add)} new question-answer pairs")
        collection.add(
            documents=questions_to_add,
            metadatas=answers_to_add,
            ids=new_ids
        )
    
    result = {
        "status": "success", 
        "message": f"Added {len(questions_to_add)} new unique question-answer pairs", 
        "new_pairs_count": len(questions_to_add),
        "duplicates_skipped": len(questions) - len(questions_to_add)
    }
    logger.info(f"Batch addition result: {result}")
    return result

class GoogleSheetInfo(BaseModel):
    sheet_id: str
    gid: str
    collection: Optional[str] = None
    question_column: Optional[str] = 'question'
    answer_column: Optional[str] = 'answer'

@app.post("/add_from_sheet")
async def add_data_from_sheet(sheet_info: GoogleSheetInfo):
    logger.info(f"Adding data from Google Sheet: {sheet_info}")
    try:
        url = f'https://docs.google.com/spreadsheets/d/{sheet_info.sheet_id}/gviz/tq?tqx=out:csv&gid={sheet_info.gid}'
        logger.info(f"Fetching data from URL: {url}")
        response = requests.get(url)
        response.encoding = 'utf-8'
        df = pd.read_csv(io.StringIO(response.text), header=[0])
        logger.info(f"Data fetched successfully. Shape: {df.shape}")
        
        logger.info(f"Available columns: {df.columns.tolist()}")
        
        if sheet_info.question_column in df.columns and sheet_info.answer_column in df.columns:
            question_column = sheet_info.question_column
            answer_column = sheet_info.answer_column
        else:
            if len(df.columns) < 2:
                raise ValueError("Sheet must contain at least two columns")
            question_column = df.columns[0]
            answer_column = df.columns[1]
            logger.warning(f"Columns '{sheet_info.question_column}' and '{sheet_info.answer_column}' not found. "
                           f"Using '{question_column}' for questions and '{answer_column}' for answers")
        
        questions = df[question_column].to_list()
        answers = df[answer_column].to_list()
        
        result = batch_addition(questions, answers, sheet_info.collection)
        logger.info(f"Data added from sheet. Result: {result}")
        return {
            **result,
            "total_rows_in_sheet": len(questions),
            "used_question_column": question_column,
            "used_answer_column": answer_column
        }
    except Exception as e:
        logger.error(f"Error processing Google Sheet: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing Google Sheet: {str(e)}")

@app.post("/batch_add")
async def batch_add(batch_data: BatchAddition):
    logger.info(f"Received batch addition request: {len(batch_data.questions)} questions")
    return batch_addition(batch_data.questions, batch_data.answers, batch_data.collection)

@app.post("/clear_collection")
async def clear_collection(collection_name: Optional[str] = None):
    logger.info(f"Clearing collection: {collection_name or 'default'}")
    try:
        collection = chroma_client.get_collection(collection_name) if collection_name else default_collection
        all_ids = collection.get()["ids"]
        logger.info(f"Deleting {len(all_ids)} items from collection")
        collection.delete(all_ids)
        return {"status": "success", "message": f"Коллекция {collection.name} очищена"}
    except Exception as e:
        logger.error(f"Error clearing collection: {str(e)}", exc_info=True)
        return {"status": "error", "message": f"Ошибка при очистке коллекции: {str(e)}"}

@app.post("/drop_collection")
async def drop_collection(collection_name: str):
    logger.info(f"Dropping collection: {collection_name}")
    try:
        chroma_client.delete_collection(collection_name)
        logger.info(f"Collection {collection_name} dropped successfully")
        return {"status": "success", "message": f"Коллекция {collection_name} удалена"}
    except Exception as e:
        logger.error(f"Error dropping collection: {str(e)}", exc_info=True)
        return {"status": "error", "message": f"Ошибка при удалении коллекции: {str(e)}"}

@app.post("/reset_database")
async def reset_database():
    logger.info("Starting database reset")
    global chroma_client, default_collection
    try:
        collections = chroma_client.list_collections()
        logger.info(f"Found {len(collections)} collections")
        
        for collection in collections:
            try:
                logger.info(f"Clearing collection {collection.name}")
                all_ids = collection.get()["ids"]
                if all_ids:
                    logger.info(f"Deleting {len(all_ids)} items from collection {collection.name}")
                    collection.delete(ids=all_ids)
                else:
                    logger.info(f"Collection {collection.name} is already empty")
            except Exception as e:
                logger.error(f"Error clearing collection {collection.name}: {str(e)}", exc_info=True)

        logger.info("Recreating Chroma client")
        chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        
        for collection in chroma_client.list_collections():
            try:
                logger.info(f"Deleting collection: {collection.name}")
                chroma_client.delete_collection(collection.name)
            except Exception as e:
                logger.error(f"Error deleting collection {collection.name}: {str(e)}", exc_info=True)

        logger.info("Creating new default collection")
        default_collection = get_or_create_collection()
        
        logger.info("Database reset completed successfully")
        return {"status": "success", "message": "База данных сброшена, все коллекции очищены"}
    except Exception as e:
        logger.error(f"Error resetting database: {str(e)}", exc_info=True)
        return {"status": "error", "message": f"Ошибка при сбросе базы данных: {str(e)}"}

@app.get("/view_top_n")
async def view_top_n(n: int = 10, collection_name: Optional[str] = None):
    logger.info(f"Viewing top {n} items from collection: {collection_name or 'default'}")
    try:
        collection = chroma_client.get_collection(collection_name) if collection_name else default_collection
        logger.info(f"Collection retrieved: {collection.name}")
        
        results = collection.get(limit=n, include=['metadatas', 'documents'])  # Добавляем 'documents'
        logger.info(f"Results retrieved: {results}")
        
        if not results or not isinstance(results, dict):
            logger.warning(f"Unexpected results format: {results}")
            return {"error": "No results or unexpected format", "results": str(results)}
        
        items = []
        for i in range(len(results.get('ids', []))):
            item = {
                "id": results['ids'][i] if 'ids' in results else f"item_{i}",
                "question": results.get('documents', [])[i] if results.get('documents') and i < len(results.get('documents', [])) else "No question available",
                "answer": results.get('metadatas', [])[i].get("answer", "No answer available") if results.get('metadatas') and i < len(results.get('metadatas', [])) else "No answer available"
            }
            items.append(item)
        
        logger.info(f"Processed {len(items)} items")
        return {
            "total_items": len(items),
            "items": items
        }
    except Exception as e:
        logger.error(f"Error viewing top N items: {str(e)}", exc_info=True)
        return {"error": str(e), "traceback": traceback.format_exc()}
    
@app.get("/count_items")
async def count_items(collection_name: Optional[str] = None):
    logger.info(f"Counting items in collection: {collection_name or 'default'}")
    try:
        collection = chroma_client.get_collection(collection_name) if collection_name else default_collection
        count = collection.count()
        logger.info(f"Item count: {count}")
        return {"collection_name": collection_name or "default", "item_count": count}
    except Exception as e:
        logger.error(f"Error counting items: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error counting items: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
