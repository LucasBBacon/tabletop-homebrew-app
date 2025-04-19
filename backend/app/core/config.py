import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.getenv("ENV_FILE_PATH", ".env"))

class Settings(BaseSettings):
    APP_NAME : str = "My FastAPI App"
    APP_VERSION : str = "1.0.0"    
    ALGORITHM : str = "HS256"
    DATABASE_URL : str
    SECRET_KEY : str
    ACCESS_TOKEN_EXPIRE_MINUTES : int
    DEBUG : bool

    AUTH_PREFIX : str
    USERS_PREFIX : str
    
    
    class Config:
        env_file = ".env"
    
settings = Settings()