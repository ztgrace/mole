from lib.config import Config
from time import time
from flask import Flask
from lib.server.checkin import log_event
import io
import re
import sys
from twisted.internet import reactor, defer, endpoints
from twisted.logger import jsonFileLogObserver, Logger, globalLogBeginner, textFileLogObserver
from twisted.logger import LogLevelFilterPredicate, LogLevel
from twisted.names import client, dns, error, server
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource
from twisted.names.dns import Message
from twisted.names.authority import FileAuthority

log = Logger(namespace='mole.dns')
mole_config = Config()
pattern = None


class MoleDNSServerFactory(server.DNSServerFactory):
    def buildProtocol(self, addr):
        return server.DNSServerFactory.buildProtocol(self, addr)


class MoleDNSDatagramProtocol(dns.DNSDatagramProtocol):
    def datagramReceived(self, datagram, addr):
        requester = f'{addr[0]}:{addr[1]}'
        log.info("Datagram to DNSDatagramProtocol from {}".format(requester))

        # Parse the datagram and log if it's a match
        m = Message()
        m.fromStr(datagram)
        for q in m.queries:
            log.info(f'datagramReceived: {q.name.name}')
            match = check_pattern(q.name.name)
            if match:
                log.info('datagramReceived: matched')
                log_event(mole_config, match['token'], 'dns', {'fqdn': q.name.name.decode("utf-8"), 'requester': requester})

        return dns.DNSDatagramProtocol.datagramReceived(self, datagram, addr)


def check_pattern(name):
    global pattern
    log.debug(f'check_pattern name: {name}')
    log.debug(f'check_pattern name type: {type(name)}')
    log.debug(f'check_pattern name reversed: {name[::-1]}')
    log.debug(f'check_pattern pattern: {pattern.pattern}')

    # reverse the domain then check the regex
    match = pattern.match(name[::-1])
    if match:
        log.info(f'check_pattern match: {match}')
        token = match.group('token')[::-1]
        extra = match.group('extra')[::-1]

        return {'name': bytes(name),
                'token': token,
                'extra': extra}

    return False


class DynamicAuthority(FileAuthority):
    def __init__(self, **kwargs):
        super(FileAuthority, self).__init__()
        self.soa = dns.Record_SOA(
            mname=kwargs['mname'],
            rname=kwargs['rname'],
            serial=int(time()),
            refresh=kwargs['refresh'],
            retry=kwargs['retry'],
            expire=kwargs['expire'],
            minimum=kwargs['minimum'],
        )

    def setupConfigNamespace(self):
        pass

    def encode(self, body_tmp, compDict):
        pass


class DynamicResolver(object):
    def __init__(self, config):
        self.config = config
        self.log = Logger(namespace='mole.dns')
        self.authority = DynamicAuthority(**{
            'data': None,
            'mname': self.config.token_domain,
            'rname': '',
            'refresh': 86400,
            'retry': 7200,
            'expire':  3600000,
            'minimum': 1800,
        })

    def _handleResponse(self, match):
        #log.debug(f'_handleResponse match: {match}')
        address = self.config.dns_addr
        log.debug(f'_handleResponse address: {address}')
        answer = dns.RRHeader(
            name=match['name'],
            payload=dns.Record_A(address=address),
            auth=True
        )
        answer.auth = True
        answers = [answer]
        authority = []
        additional = []
        return answers, authority, additional

    def query(self, query, timeout=None):
        match = check_pattern(query.name.name)
        #log.debug(f'query match: {str(match)}')
        log.debug(f'query type: {query.type}')

        if match and (query.type == dns.A or query.type == dns.AAAA):
            # if match:
            self.log.info('success')
            return defer.succeed(self._handleResponse(match))
        else:
            # return defer.fail(error.DomainError())
            self.log.info('fail')
            return defer.fail(error.DomainError())


def launch(config: Config, app: Flask):
    global mole_config
    global pattern
    mole_config = config

    # reverse the domain and escape periods so it's easier to regex
    pattern = re.compile(
        br'^%s\.(?P<token>[a-zA-Z0-9\-]+)\.?(?P<extra>.*)$' % mole_config.token_domain[::-1].replace('.', '\.').encode(
            'utf-8'))

    # Configure logging
    if config.debug:
        info_predicate = LogLevelFilterPredicate(LogLevel.debug)
    info_predicate = LogLevelFilterPredicate(LogLevel.info)
    log = Logger(LogLevel.debug)
    observers = [textFileLogObserver(sys.stdout),
                 jsonFileLogObserver(io.open("server.json", "a"))]
    globalLogBeginner.beginLoggingTo(observers)

    # Configure DNS server
    dns_factory = MoleDNSServerFactory(
        clients=[DynamicResolver(config)]
    )

    dns_protocol = MoleDNSDatagramProtocol(controller=dns_factory)
    reactor.listenUDP(mole_config.server_dns_port, dns_protocol)
    reactor.listenTCP(mole_config.server_dns_port, dns_factory)

    # Configure HTTP server
    log.info(f'Launching API with API_KEY: {app.config.get("API_KEY")}')
    resource = WSGIResource(reactor, reactor.getThreadPool(), app)

    endpoint_description = "tcp:port=%i:interface=0.0.0.0" % mole_config.server_web_port
    endpoint = endpoints.serverFromString(reactor, endpoint_description)
    endpoint.listen(Site(resource))

    reactor.run()


if __name__ == '__main__':
    raise SystemExit(launch())
