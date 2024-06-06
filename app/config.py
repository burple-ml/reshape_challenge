# initialisations

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import urllib.parse
from dotenv import load_dotenv 

load_dotenv()

base_path = "./app"
IMAGE_OPS_SCHEMA = "image_ops"


class InitialisationException(Exception):
    def __init__(self, message) -> None:
        print("One or more environment variables were not set: " +  str(message))


try:
    host = os.environ['DBHOSTNAME']
    password = urllib.parse.quote_plus(os.environ['DBPASSWORD'])
    username = os.environ['DBUSERNAME']
    dbname = os.environ['DBNAME']
    port = int(os.environ['DBPORT']) 
    schema = IMAGE_OPS_SCHEMA
except KeyError as e:
    raise InitialisationException(str(e))

engine = create_engine(f'postgresql+psycopg://{username}:{password}@{host}:{port}/{dbname}', echo=True) 

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def setup_database():
    with engine.connect() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {IMAGE_OPS_SCHEMA};"))
        conn.execute(text(f'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
        conn.commit()

    # Create tables if not exists
    Base.metadata.create_all(bind=engine)