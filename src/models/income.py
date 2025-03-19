from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from .base import Base

class Income(Base):
    __tablename__ = 'income'
    
    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    source = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<Income(amount={self.amount}, source='{self.source}')>"