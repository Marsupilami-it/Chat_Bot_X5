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

app = FastAPI()
os.environ['HF_HUB_DOWNLOAD_TIMEOUT'] = '500'

CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "/app/data/chroma")
HF_HOME = os.getenv("HF_HOME", "/root/.cache/huggingface")

chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="WpythonW/RUbert-tiny_custom_test_2",
    cache_folder=HF_HOME
)

# Получаем размерность эмбеддингов
EMBEDDING_DIMENSION = len(emb_fn("test"))

def get_or_create_collection(name="corpus"):
    try:
        return chroma_client.get_collection(name=name, embedding_function=emb_fn)
    except ValueError:
        return chroma_client.create_collection(
            name=name,
            embedding_function=emb_fn,
            metadata={"hnsw:space": "cosine", "dimension": EMBEDDING_DIMENSION}
        )

default_collection = get_or_create_collection()

class Query(BaseModel):
    queries: List[str]
    n_results: int = 3

class GoogleSheetInfo(BaseModel):
    sheet_id: str
    gid: str
    collection: Optional[str] = None

class BatchAddition(BaseModel):
    documents: List[str]
    metadatas: List[dict]
    collection: Optional[str] = None


@app.post("/api/v1/get_answer/")
async def query(query_data: Query):
    try:
        results = default_collection.query(
            query_texts=query_data.queries,
            n_results=query_data.n_results
        )
        return {"answer": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

def batch_addition(documents, metadatas, collection_name=None):
    collection = get_or_create_collection(collection_name) if collection_name else default_collection
    
    # Получаем существующие документы
    existing_docs = collection.get(include=['documents'])
    existing_contents = set(existing_docs['documents'])
    
    # Создаем словарь для отслеживания уникальных документов в новой партии
    unique_docs = {}
    documents_to_add = []
    metadatas_to_add = []
    
    for doc, meta in zip(documents, metadatas):
        # Проверяем, не является ли документ дубликатом существующего или уже добавленного
        if doc not in existing_contents and doc not in unique_docs:
            documents_to_add.append(doc)
            metadatas_to_add.append(meta)
            unique_docs[doc] = True
    
    if documents_to_add:
        new_ids = [str(i) for i in range(len(existing_contents), len(existing_contents) + len(documents_to_add))]
        collection.add(
            documents=documents_to_add,
            metadatas=metadatas_to_add,
            ids=new_ids
        )
    
    return {
        "status": "success", 
        "message": f"Added {len(documents_to_add)} new unique documents", 
        "new_docs_count": len(documents_to_add),
        "duplicates_skipped": len(documents) - len(documents_to_add)
    }

@app.post("/add_from_sheet")
async def add_data_from_sheet(sheet_info: GoogleSheetInfo):
    try:
        url = f'https://docs.google.com/spreadsheets/d/{sheet_info.sheet_id}/gviz/tq?tqx=out:csv&gid={sheet_info.gid}'
        response = requests.get(url)
        response.encoding = 'utf-8'
        df = pd.read_csv(io.StringIO(response.text), header=[0])
        
        content_column = 'content' if 'content' in df.columns else df.columns[0]
        
        if 'category' in df.columns:
            documents = df[content_column].to_list()
            metadatas = [{'category': category} for category in df['category']]
        else:
            documents = df[content_column].to_list()
            metadatas = [{'category': 'default'} for _ in range(len(documents))]
        
        result = batch_addition(documents, metadatas, sheet_info.collection)
        return {
            **result,
            "total_rows_in_sheet": len(documents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing Google Sheet: {str(e)}")
    

@app.post("/batch_add")
async def batch_add(batch_data: BatchAddition):
    return batch_addition(batch_data.documents, batch_data.metadatas, batch_data.collection)

@app.post("/clear_collection")
async def clear_collection(collection_name: Optional[str] = None):
    try:
        collection = chroma_client.get_collection(collection_name) if collection_name else default_collection
        collection.delete(collection.get()["ids"])
        return {"status": "success", "message": f"Коллекция {collection.name} очищена"}
    except Exception as e:
        return {"status": "error", "message": f"Ошибка при очистке коллекции: {str(e)}"}

@app.post("/drop_collection")
async def drop_collection(collection_name: str):
    try:
        chroma_client.delete_collection(collection_name)
        return {"status": "success", "message": f"Коллекция {collection_name} удалена"}
    except Exception as e:
        return {"status": "error", "message": f"Ошибка при удалении коллекции: {str(e)}"}

@app.post("/reset_database")
async def reset_database():
    global chroma_client, default_collection
    try:
        # Получаем список всех коллекций
        collections = chroma_client.list_collections()
        
        # Удаляем содержимое каждой коллекции
        for collection in collections:
            try:
                all_ids = collection.get()["ids"]
                if all_ids:
                    collection.delete(ids=all_ids)
            except Exception as e:
                print(f"Ошибка при очистке коллекции {collection.name}: {str(e)}")

        # Пересоздаем клиент
        chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        
        # Попытка удалить все коллекции
        for collection in chroma_client.list_collections():
            try:
                chroma_client.delete_collection(collection.name)
            except Exception as e:
                print(f"Ошибка при удалении коллекции {collection.name}: {str(e)}")

        # Создаем новую дефолтную коллекцию
        default_collection = get_or_create_collection()
        
        return {"status": "success", "message": "База данных сброшена, все коллекции очищены"}
    except Exception as e:
        return {"status": "error", "message": f"Ошибка при сбросе базы данных: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)