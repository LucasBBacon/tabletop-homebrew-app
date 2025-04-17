from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME : str = "My FastAPI App"
    APP_VERSION : str = "1.0.0"
    DEBUG : bool = True
    
    DATABASE_URL : str = "postgresql+psycopg2://myappuser:myappuserpassword@db:5432/tabletop_db"

    SECRET_KEY : str = "your_secret_key"
    ALGORITHM : str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES : int = 30    
    
    AUTH_PREFIX : str = "/auth"
    USERS_PREFIX : str = "/users"
    
    class Config:
        env_file = ".env"
    
settings = Settings()