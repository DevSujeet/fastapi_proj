
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import urllib
from src.config.configs import _db_settings
from src.config.log_config import logger

# from sqlmodel import create_engine as create_sqlmodel_engine, SQLModel, Session

db_settings_instance = _db_settings()

###---------------------------------------
# postgresql+asyncpg://username:password@hostname:port/databasename

ASYNC_DATABASE_URL = f'postgresql+asyncpg://{db_settings_instance.db_username}' \
                        f':{db_settings_instance.db_password}@{db_settings_instance.db_host}:5432/{db_settings_instance.db_name}'
logger.debug(f'DATABASE_USERNAME: {db_settings_instance.db_username}')
logger.debug(f'DATABASE_HOST: {db_settings_instance.db_host}')

safe_password = urllib.parse.quote_plus(db_settings_instance.db_password)

SYNC_DATABASE_URL = f'postgresql://{db_settings_instance.db_username}' \
                        f':{db_settings_instance.db_password}@{db_settings_instance.db_host}:5432/{db_settings_instance.db_name}'

###----------------------sqlalchmy base-----------------

LOCAL_DATABASE = 'sqlite:///db_test.sqlite'
# engine = create_engine(LOCAL_DATABASE)
engine = create_engine(SYNC_DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base object
Base = declarative_base()


@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
    except:
        session.rollback()
        raise
    finally:
        session.close()

# To create all the table defined as models
def init_db():
    print(f'table that are getting created are: {Base.metadata.tables.keys()}')
    try:
        Base.metadata.create_all(engine)
        print("Tables created successfully.")
    except Exception as e:
        print("Error while creating tables:", e)

#--------SQLMODEL based--------------------
# SQLModel.metadata = Base.metadata
# LOCAL_DATABASE = 'sqlite:///db.sqlite'
# engine_sqlModel = create_sqlmodel_engine(LOCAL_DATABASE, echo=True)

# def init_db():
#     SQLModel.metadata.create_all(engine_sqlModel)

# def get_session():
#     with Session(engine_sqlModel) as session:
#         yield session