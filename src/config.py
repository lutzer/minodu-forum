import os
from dotenv import load_dotenv

load_dotenv()

config = None
class Config:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup()
        return cls._instance
    
    def _setup(self):
        self._port = None
        self._api_prefix = None
        self._database_url = None
        self._jwt_secret = None
        self._jwt_algorithm = None

    @property
    def port(self):
        if self._port is None:
            self._port = int(os.getenv("PORT", 3001))
        return self._port

    @property
    def api_prefix(self):
        if self._api_prefix is None:
            self._api_prefix = os.getenv("API_PREFIX", "/forum")
        return self._api_prefix

    @property
    def database_url(self):
        if self._database_url is None:
            self._database_url = os.getenv("DATABASE_URL", "sqlite:///./database.db")
        return self._database_url

    @property
    def jwt_secret(self):
        if self._jwt_secret is None:
            self._jwt_secret = os.getenv("JWT_SECRET_KEY", "not a safe key")
        return self._jwt_secret

    @property
    def jwt_algorithm(self):
        if self._jwt_algorithm is None:
            self._jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        return self._jwt_algorithm      