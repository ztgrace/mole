from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

global mole_config
engine = create_engine('sqlite:///mole.db', convert_unicode=True)
#engine = create_engine(mole_config.db_conn, convert_unicode=True)
db = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db.query_property()

# Import subclasses
from lib.models.event import Event
from lib.models.token import Token

Base.metadata.create_all(bind=engine)
