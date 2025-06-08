from pydantic import Extra
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """ Класс настроек для работы проекта. """
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    OPENAI_API_KEY: str
    LLM_PROVIDER: str = "deepseek"

    model_config = SettingsConfigDict(
        env_file=(".env", ".test.env"),
        extra=Extra.allow
    )


settings = Settings()


def get_db_url():
    """
    Формирует строку подключения к базе данных PostgreSQL с использованием asyncpg.

    :return: Строка подключения к базе данных в формате
             'postgresql+asyncpg://<user>:<password>@<host>:<port>/<dbname>'
    :rtype: str
    """
    return (
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
        f"{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )


def get_api_key():
    return settings.OPENAI_API_KEY


database_url = get_db_url()
api_key = get_api_key()
