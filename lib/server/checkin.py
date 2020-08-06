from datetime import datetime
import json
from lib.config import Config
from lib.models import *
from lib.models.event import Event
from lib.models.token import Token
from twisted.logger import Logger


def log_event(config: Config, token: Token, etype, ctx: dict):
    log = Logger()
    if type(token) is str:
        token = token.encode('utf-8')
        log.debug('token: ' + token.decode('utf-8'))
    t = Token.query.filter_by(token=token.decode("utf-8")).first()
    if t is None:
        log = Logger()
        log.error('Unable to find %s token' % token.decode("utf-8"))
        return

    e = Event(type=etype,
              token_id=t.id,
              token=t,
              timestamp=datetime.utcnow(),
              context=json.dumps(ctx))
    db.add(e)
    db.commit()

    message = f"""
DNS Checkin
Date: {e.timestamp} UTC
Token: {t.token}
Tags: {t.context}
Context: {json.dumps(ctx)}
"""
    print(config.notifications)
    for n in config.notifications:
        if not n.isEnabled():
            continue
        try:
            res = n.notify(message)
            print(res)
            print(res.request)
        except:
            log.error('error executing notify class %s' % n)
