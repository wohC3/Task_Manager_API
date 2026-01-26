from fastapi import FastAPI
from contextlib import asynccontextmanager

from .database import create_db_and_tables, SessionDep
from .models import Task
@asynccontextmanager 
async def lifespan(app: FastAPI):
    create_db_and_tables() 
    yield 

app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return{"message":"Task manager API is running"}
