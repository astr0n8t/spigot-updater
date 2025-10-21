"""
Database models and initialization
"""
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

Base = declarative_base()

class ServerJar(Base):
    """Server jar model"""
    __tablename__ = 'server_jars'
    
    id = Column(Integer, primary_key=True)
    type = Column(String(50))
    version = Column(String(50))
    latest_version = Column(String(50))
    latest_build = Column(String(50))
    latest_file = Column(String(255))
    latest_checksum = Column(String(255))
    approved_version = Column(String(50))
    approved_build = Column(String(50))
    approved_file = Column(String(255))
    approved_checksum = Column(String(255))
    downloaded = Column(String(50))

class Plugin(Base):
    """Plugin model"""
    __tablename__ = 'plugins'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    latest = Column(String(50))
    approved = Column(String(50))
    downloaded = Column(String(50))

class Server(Base):
    """Server model"""
    __tablename__ = 'servers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    current = Column(String(50))
    plugins = Column(Text, default='{}')

def init_database(log):
    """Initialize database and return models"""
    log.info('Connecting to database')
    
    # Create engine
    db_path = Path(__file__).parent.parent.parent / 'data' / 'database.sqlite'
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    
    # Create tables
    Base.metadata.create_all(engine)
    
    # Create session factory
    Session = sessionmaker(bind=engine)
    
    return {
        'engine': engine,
        'Session': Session,
        'ServerJars': ServerJar,
        'Plugins': Plugin,
        'Servers': Server
    }
