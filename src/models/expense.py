from sqlalchemy import Column, Integer, Float, String, DateTime, LargeBinary
from datetime import datetime
from .base import Base

class Expense(Base):
    __tablename__ = 'expenses'
    
    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    category = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.now)
    receipt_image = Column(LargeBinary, nullable=True)
    
    def __repr__(self):
        return f"<Expense(amount={self.amount}, description='{self.description}')>"