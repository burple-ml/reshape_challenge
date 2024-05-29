# centralised initialisation script 

import os
from sqlalchemy import create_engine

base_path = "./app"

class InitialisationException(Exception):
    def __init__(self, message) -> None:
        print("One or more environment variables were not set: " +  str(message))


class DatabaseConnector():
    def __init__(self) -> None:
        try:    
            import urllib.parse
            host = os.environ['DBHOSTNAME']
            password = urllib.parse.quote_plus(os.environ['DBPASSWORD'])
            username = os.environ['DBUSERNAME']
            dbname = os.environ['DBNAME']
            port = int(os.environ['DBPORT'])      #postgres
            engine = create_engine(f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{dbname}')
            print(engine)
        except KeyError as e:
            raise InitialisationException(str(e))
        

db_conn = DatabaseConnector()