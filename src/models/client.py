from sqlalchemy import Column, Integer, String
from .base import Base

class Client(Base):
    __tablename__ = 'clients'
    
    id = Column(Integer, primary_key=True)
    business_name = Column(String, nullable=False)
    poc = Column(String, nullable=True)  # Point of Contact
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<Client(business_name='{self.business_name}', email='{self.email}')>"