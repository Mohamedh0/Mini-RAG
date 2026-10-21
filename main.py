from fastapi import FastAPI

from mini_rag.routes import base, data, nlp
from motor.motor_asyncio import AsyncIOMotorClient
from src.mini_rag.helpers.config import get_settings
from src.mini_rag.stores.llm.LLMProviderFactory import LLMProviderFactory
from src.mini_rag.stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from src.mini_rag.stores.llm.templates.template_parser import TemplateParser
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    mongo_conn = AsyncIOMotorClient(
        settings.MONGODB_URL,
        serverSelectionTimeoutMS=5000,
    )
    app.state.vectordb_client = None

    try:
        await mongo_conn.admin.command("ping")

        app.state.mongo_conn = mongo_conn
        app.state.db_client = mongo_conn[settings.MONGODB_DATABASE]

        llm_provider_factory = LLMProviderFactory(settings)
        vectordb_provider_factory = VectorDBProviderFactory(settings)

        app.state.generation_client = llm_provider_factory.create(
            provider=settings.GENERATION_BACKEND
        )
        app.state.generation_client.set_generation_model(
            model_id=settings.GENERATION_MODEL_ID
        )

        app.state.embedding_client = llm_provider_factory.create(
            provider=settings.EMBEDDING_BACKEND
        )
        app.state.embedding_client.set_embedding_model(
            model_id=settings.EMBEDDING_MODEL_ID,
            embedding_size=settings.EMBEDDING_MODEL_SIZE,
        )

        app.state.vectordb_client = vectordb_provider_factory.create(
            provider=settings.VECTOR_DB_BACKEND
        )
        app.state.vectordb_client.connect()

        app.state.template_parser = TemplateParser(
            language=settings.PRIMARY_LANG,
            default_language=settings.DEFAULT_LANG,
        )

        yield

    finally:
        mongo_conn.close()
        if app.state.vectordb_client is not None:
            app.state.vectordb_client.disconnect()


app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
