import os
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
import json

load_dotenv()


mongo_uri=os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

client=MongoClient(mongo_uri)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

app = FastAPI()


#Modelo para actualizar la disponiblilidad

class UpdateAvailability(BaseModel):
    id: str
    available : bool


@app.get("/")
def read_root():
    return {"message": "API funcionando correctamente 🚀"}

@app.get("/horarios_disponibles", response_model=List[dict[str, str]])  # 🔹 Ahora devuelve una lista de diccionarios
def get_horarios_disponibles():
    horarios_disponibles = list(collection.find({"available": True}, {"date": 1, "time": 1, "_id": 1}))

    if not horarios_disponibles:
        raise HTTPException(status_code=404, detail="No hay horarios disponibles")

    # Convertimos el ObjectId en string y estructuramos el JSON
    lista_horarios = [
        {"id": str(doc["_id"]), "fecha": doc["date"], "hora": doc["time"]}
        for doc in horarios_disponibles
    ]

    return lista_horarios


@app.post("/actualizar_disponibilidad")
def actualizar_disponibilidad(data: UpdateAvailability):
    resultado = collection.update_one({"_id": ObjectId(data.id)}, {"$set": {"available": data.available}})

    if resultado.modified_count == 0:
        raise HTTPException(status_code=404, detail="No se encontró el horario")
    
    return {"message": "Disponibilidad actualizada correctamente"}