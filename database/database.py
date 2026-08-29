from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
import os

def init_database():
    """Initialize the database"""
    db_path = os.path.join(os.path.dirname(__file__), 'healthcare.db')
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    Base.metadata.create_all(engine)
    return engine

def get_db_session():
    """Get database session"""
    from .models import get_session
    return get_session()