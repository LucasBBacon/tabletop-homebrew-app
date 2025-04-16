class settings:
    APP_NAME = "My FastAPI App"
    APP_VERSION = "1.0.0"
    DEBUG = True
    DATABASE_URL = "sqlite:///./test.db"
    API_PREFIX = "/api/v1"
    AUTH_PREFIX = "/auth"
    USERS_PREFIX = "/users"
    
SECRET_KEY = "waucydelgaucy"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30