from fastapi import FastAPI

from mini_rag.routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from src.mini_rag.helpers.config import get_settings
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    app.state.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.state.db_client = app.state.mongo_conn[settings.MONGODB_DATABASE]

    try:
        # Application runs while execution is paused here.
        yield
    finally:
        app.state.mongo_conn.close()


app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)
