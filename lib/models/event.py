from lib.models import *
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship, backref


class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    type = Column(String(256))
    timestamp = DateTime()

    token_id = Column(Integer, ForeignKey('tokens.id'),
                      nullable=False)
    token = relationship('Token',
                         backref=backref('events', lazy=True))

    # Context about the event such as source IP address
    context = Column(Text)

    def __repr__(self):
        return '<Event token:%s, ts:%s>' % (self.token, self.timestamp)
