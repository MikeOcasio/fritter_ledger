from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from ..models.base import Base
import configparser
import os

class DatabaseManager:
    def __init__(self):
        config = configparser.ConfigParser()
        # Get the absolute path to config.ini
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.ini')
        config.read(config_path)
        
        # Create PostgreSQL URL
        db_url = f"postgresql://{config['Database']['user']}:{config['Database']['password']}@{config['Database']['host']}:{config['Database']['port']}/{config['Database']['dbname']}"
        
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        
    def init_db(self):
        Base.metadata.create_all(self.engine)
        
    def get_session(self):
        return self.Session()
    
    def add_record(self, record):
        session = self.get_session()
        try:
            session.add(record)
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error adding record: {str(e)}")
            return False
        finally:
            session.close()