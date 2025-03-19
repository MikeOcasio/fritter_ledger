from sqlalchemy import Column, Integer, Float, String, DateTime, Date
from datetime import datetime
from .base import Base

class Subscription(Base):
    __tablename__ = 'subscriptions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    billing_cycle = Column(String, nullable=False)  # monthly, yearly, etc.
    next_billing_date = Column(Date, nullable=False)
    
    def __repr__(self):
        return f"<Subscription(name='{self.name}', amount={self.amount})>"