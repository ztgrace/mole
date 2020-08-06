from datetime import datetime
from lib.models import *
from lib.server.checkin import log_event
from lib.util import token_from_hostname
import json
import string
import random
from flask import Flask, jsonify, request, Response, abort, make_response
from lib.util import get_version

app = Flask('mole')


def _parse_uri(self, uri, ctx):
    segments = uri.split('/')

    match = self._token_pattern.match(segments[1])
    if segments[1] == 'token':
        ctx['type'] = 'token'
    elif match:
        ctx['type'] = 'checkin'
        ctx['token'] = match.group('token')

    return ctx


def _validate_token(self, token):
    """
    Call out to the storage service and validate the token
    :param token:
    :return:
    """
    pass


def _store_token(t, ctx):
    t = Token(token=t, context=json.dumps(ctx), created=datetime.utcnow())
    # t.context = json.dumps(ctx)
    db.add(t)
    db.commit()


@app.route('/token', methods=['POST'])
def _token():
    api_token = request.headers.get('X-API-Key')  # TODO: move to a decorator
    if not api_token == app.config['API_KEY']:
        abort(401)

    ctx = json.loads(request.json)
    t = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(ctx['token_length']))
    ctx['requester'] = request.remote_addr
    _store_token(t, ctx)
    print('token: {}'.format(t))
    return jsonify({'token': t})

@app.errorhandler(401)
def custom_401(error):
    return Response('Unauthorized', 401)

@app.route('/health', methods=['GET'])
def _health():
    # request.setHeader('Content-Type', 'application/json')
    return jsonify({'all_good': True})


@app.route('/checkin/<token>', methods=['GET'])
def checkin(token):
    ctx = {'requester': request.remote_addr, 'raw_request': str(request.headers)}

    api_token = request.headers.get('X-API-Key') # TODO: move to a decorator
    if not api_token == app.config['API_KEY']:
        abort(401)

    log_event(app.config['mole_config'], 'web', token, ctx)

    return 'Checked in %s' % token


@app.route('/', methods=['GET'])
def index():
    return 'Mole Server v%s' % get_version()


@app.route('/xss')
def xss_file_handler():

    if request.headers.get('host', None):
        ctx = {'requester': request.remote_addr, 'raw_request': str(request.headers)}
        token = token_from_hostname(request.headers.get('host'))
        log_event(app.config['mole_config'], token, 'xss checkin', ctx)

    js = open("plugins/payloads/xss/xss.js", "r").read()
    res = make_response(js)
    res.mimetype = 'application/javascript'
    return res
