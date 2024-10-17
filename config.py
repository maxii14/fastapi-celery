from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASS: str
    PKCS11_LIB_PATH: str
    TOKEN_LABEL: str
    TOKEN_PASS: str
    TOKEN_KEY_LABEL: str
    CELERY_BROKER_URL: str
    CELERY_BACKEND_URL: str
    GENERATING_PACKAGE_SIZE: int

    def get_db_url(self):
        return f'postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    # Берём значения из .env
    model_config = SettingsConfigDict(env_file='.env')

settings = Settings()
