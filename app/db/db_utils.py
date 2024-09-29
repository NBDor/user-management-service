import threading
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from typing import Optional


class DatabaseConnectionPool:
    _instance: Optional["DatabaseConnectionPool"] = None
    _lock: threading.Lock = threading.Lock()
    engine: Engine
    session_local: sessionmaker[Session]

    def __new__(cls) -> "DatabaseConnectionPool":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DatabaseConnectionPool, cls).__new__(cls)
                    cls._instance._initialize_pool()
        return cls._instance

    def _initialize_pool(self) -> None:
        self.engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
        self.session_local = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def get_session(self) -> Session:
        return self.session_local()
