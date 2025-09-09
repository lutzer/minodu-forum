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
        self._upload_dir = None
        self._max_file_size = None
        self._service_url = None
        self._avatar_dir = None

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
    def service_url(self):
        if self._service_url is None:
            self._service_url = os.getenv("AI_SERVICE_URL", "/services")
        return self._service_url
    
    @property
    def upload_dir(self):
        if self._upload_dir is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            upload_dir = os.getenv("UPLOAD_DIR", "uploads")
            self._upload_dir = os.path.join(script_dir, "..", upload_dir)
        return self._upload_dir
    
    @property
    def avatar_dir(self):
        if self._upload_dir is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            upload_dir = os.getenv("AVATAR_UPLOAD_DIR", "avatars")
            self._avatar_dir = os.path.join(script_dir, "..", upload_dir)
        return self._avatar_dir

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

    @property
    def max_file_size(self):
        if self._max_file_size is None:
            self._max_file_size = os.getenv("MAX_FILE_SIZE", 1024 * 1024 * 5)
        return self._max_file_size        