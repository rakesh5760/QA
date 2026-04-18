from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from backend.database.db import Base

class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(255), nullable=False)
    result_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
