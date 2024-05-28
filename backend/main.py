from fastapi import FastAPI
from api import router
from db import db, metadata, engine
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config import producer

app = FastAPI()
origins = ["http://localhost:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["get"],
    allow_headers=["*"],
)

metadata.create_all(engine)
app.state.database = db


@app.on_event("startup")
async def startup() -> None:
    db_ = app.state.database
    if not db_.is_connected:
        await db_.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    db_ = app.state.database
   # producer.close()
    if db_.is_connected:
        await db_.disconnect()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router)