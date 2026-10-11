from fastapi import FastAPI

from mini_rag.routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from src.mini_rag.helpers.config import get_settings
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    mongo_conn = AsyncIOMotorClient(
        settings.MONGODB_URL,
        serverSelectionTimeoutMS=5000,
    )

    try:
        # Verify that MongoDB is reachable.
        await mongo_conn.admin.command("ping")

        app.state.mongo_conn = mongo_conn
        app.state.db_client = mongo_conn[settings.MONGODB_DATABASE]

        yield
    finally:
        mongo_conn.close()


app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)
