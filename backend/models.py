from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


# NOTE: SQLite for MVP; can be switched to MySQL by changing SQLALCHEMY_DATABASE_URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./traceability.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class UserRole(str, Enum):
    ADMIN = "admin"
    OPERATOR = "operator"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), nullable=False, default=UserRole.OPERATOR)


class BatchStatus(str, Enum):
    NORMAL = "normal"
    EXPIRED = "expired"
    RECALL = "recall"


class Batch(Base):
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String(64), unique=True, index=True, nullable=False)
    product_name = Column(String(255), nullable=False)

    # JSON-like fields stored as Text for SQLite compatibility
    origin_info = Column(Text, nullable=True)
    process_info = Column(Text, nullable=True)
    logistics_static = Column(Text, nullable=True)
    quality_report = Column(Text, nullable=True)

    scan_count = Column(Integer, nullable=False, default=0)
    status = Column(SAEnum(BatchStatus), nullable=False, default=BatchStatus.NORMAL)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    scan_logs = relationship("ScanLog", back_populates="batch")


class ScanLog(Base):
    __tablename__ = "scan_logs"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String(64), ForeignKey("batches.batch_id"), nullable=False, index=True)
    ip_address = Column(String(64), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    batch = relationship("Batch", back_populates="scan_logs")


# Dependency-style helper for FastAPI

def get_db():
    from sqlalchemy.orm import Session

    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
