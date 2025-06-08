from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from wiki_parser_app.api.v1.routers.parser import router as parser_router
from wiki_parser_app.api.v1.routers.summary import router as summary_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[dict, None]:
    """Управление жизненным циклом приложения."""
    logger.info("Инициализация приложения...")
    yield
    logger.info("Завершение работы приложения...")


def create_app() -> FastAPI:
    """
   Создание и конфигурация FastAPI приложения.

   Returns:
       Сконфигурированное приложение FastAPI
   """
    app = FastAPI(
        title="Микросервис для парсинга статей из Википедии и получения саммари для этих статей",
        lifespan=lifespan,
    )

    # Настройка CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    # Регистрация роутеров
    register_routers(app)

    return app


def register_routers(app: FastAPI) -> None:
    """Регистрация роутеров приложения."""
    # Корневой роутер
    root_router = APIRouter()

    @root_router.get("/", tags=["root"])
    def home_page():
        return {
            "message": "Добро пожаловать!",
        }

    # Подключение роутеров
    app.include_router(root_router, tags=["root"])
    app.include_router(parser_router, tags=["parser"])
    app.include_router(summary_router, tags=["summary"])


# Создание экземпляра приложения
app = create_app()
