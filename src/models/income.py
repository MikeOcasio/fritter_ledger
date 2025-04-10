from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from .base import Base

class Income(Base):
    __tablename__ = 'income'
    
    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    source = Column(String, nullable=False)
    client = Column(String, nullable=True)
    invoice_id = Column(String, nullable=True)
    contract_id = Column(String, nullable=True)
    status = Column(String, nullable=True)  # Added status field
    date = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<Income(amount={self.amount}, source='{self.source}', client='{self.client}', status='{self.status}')>"