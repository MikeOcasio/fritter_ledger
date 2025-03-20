from sqlalchemy import Column, Integer, String, DateTime, LargeBinary
from datetime import datetime
from .base import Base

class Receipt(Base):
    __tablename__ = 'receipts'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    reference_id = Column(String, nullable=True)  # Added reference ID field
    date = Column(DateTime, default=datetime.now)
    notes = Column(String, nullable=True)
    image = Column(LargeBinary, nullable=False)
    
    def __repr__(self):
        return f"<Receipt(name='{self.name}', reference_id='{self.reference_id}', date='{self.date}')>"