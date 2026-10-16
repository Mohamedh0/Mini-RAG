from fastapi import FastAPI

from mini_rag.routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from src.mini_rag.helpers.config import get_settings
from src.mini_rag.stores.llm.LLMProviderFactory import LLMProviderFactory
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    # ---- Startup ----
    mongo_conn = AsyncIOMotorClient(
        settings.MONGODB_URL,
        serverSelectionTimeoutMS=5000,
    )

    try:
        # Verify that MongoDB is reachable.
        await mongo_conn.admin.command("ping")

        app.state.mongo_conn = mongo_conn
        app.state.db_client = mongo_conn[settings.MONGODB_DATABASE]

        llm_provider_factory = LLMProviderFactory(settings)

        # generation client
        app.state.generation_client = llm_provider_factory.create(
            provider=settings.GENERATION_BACKEND
        )
        app.state.generation_client.set_generation_model(
            model_id=settings.GENERATION_MODEL_ID
        )

        # embedding client
        app.state.embedding_client = llm_provider_factory.create(
            provider=settings.EMBEDDING_BACKEND
        )
        app.state.embedding_client.set_embedding_model(
            model_id=settings.EMBEDDING_MODEL_ID,
            embedding_size=settings.EMBEDDING_MODEL_SIZE,
        )

        yield  # ---- App serves requests here ----

    finally:
        # ---- Shutdown ----
        mongo_conn.close()


app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)
