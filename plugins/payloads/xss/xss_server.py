from flask import Blueprint, request, make_response, current_app
from lib.server.checkin import log_event
from lib.util import token_from_hostname
import logging
from .xss import XSS

logger = logging.getLogger(__name__)
xss_api = Blueprint('xss', __name__)

"""
@xss_api.route('/xss')
def xss_file_handler():

    if request.headers.get('host', None):
        ctx = {'requester': request.remote_addr, 'raw_request': str(request.headers)}
        token = token_from_hostname(request.headers.get('host'))
    token = token_from_hostname(request.headers.get('host'))
    log_event(Config(conf_file='config.yml.sever'), token, 'xss checkin', {})

    js = open("xss.js", "r").read()
    res = make_response(js)
    res.mimetype = 'application/javascript'
    return res

"""

def setup(servers, payloads):
    payloads['xss'] = XSS

    return xss_api
