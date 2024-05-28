from fastapi import FastAPI
from api import video_router
from fastapi.middleware.cors import CORSMiddleware

from db import database, engine, metadata

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
app.state.database =database


app.on_event("startup")
async def startup() -> None:
    database_ = app.state.databse
    if not database_.is_connected:
        await database_.connect()


app.on_event("shutdown")
async def startup() -> None:
    database_ = app.state.databse
    if database_.is_connected:
        await database_.disconnect()


app.include_router(video_router)
