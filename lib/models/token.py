from lib.models import *
from sqlalchemy import Column, DateTime, Integer, String, Text


class Token(Base):
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True)
    token = Column(String(256), unique=True)
    context = Column(Text)
    created = DateTime()

    def __repr__(self):
        return '<Token %s>' % self.token