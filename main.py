from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from mini_rag.routes import base, data, nlp
from src.mini_rag.helpers.config import get_settings
from src.mini_rag.stores.llm.LLMProviderFactory import LLMProviderFactory
from src.mini_rag.stores.llm.templates.template_parser import TemplateParser
from src.mini_rag.stores.vectordb.VectorDBProviderFactory import (
    VectorDBProviderFactory,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    postgres_conn = (
        f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"
    )

    app.state.db_engine = create_async_engine(postgres_conn)
    app.state.db_client = sessionmaker(
        app.state.db_engine, class_=AsyncSession, expire_on_commit=False
    )
    app.state.vectordb_client = None

    try:
        # Fail fast if PostgreSQL is unreachable 
        async with app.state.db_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

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
        await app.state.db_engine.dispose()
        if app.state.vectordb_client is not None:
            app.state.vectordb_client.disconnect()


app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
