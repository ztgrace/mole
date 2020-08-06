#!/usr/bin/env python3
import argparse
from copy import deepcopy
from lib.config import Config
from lib.plugins.listpluginmixin import ListPluginMixin
from lib.trackingtoken import TrackingToken
import logging
import os
from pluginbase import PluginBase
import requests
import sys
from lib.util import get_default_user_agent_string
from flask import Flask

if __name__ == '__main__':
    from lib.banner import *
    from lib.server.dns import *
    from lib.server.web import *

    banner()

#logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('mole')
global mole_config


class Plugin(object):
    pass


def get_plugin_dirs(path=''):
    base = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'plugins', path)

    dirs = []
    for name in os.listdir(base):
        if os.path.isdir(os.path.join(base, name)) and name != '__pycache__':
            dirs.append(os.path.join(base, name))

    return dirs


def token_server_health_check(config):
    try:
        res = requests.get('%s://%s/health' % (config.token_protocol, config.token_server),
                           headers={'User-Agent': get_default_user_agent_string()})
    except:
        return False
    return res.status_code == 200


def load_plugins(servers, payloads):
    plugin_base = PluginBase(package='mole.plugins')
    plugin_source = plugin_base.make_plugin_source(
        searchpath=get_plugin_dirs(path='payloads'))

    log.debug('Plugin dirs: ' + ", ".join(get_plugin_dirs()))
    for p in plugin_source.list_plugins():
        log.debug('Loading plugin: ' + p)
        plugin = plugin_source.load_plugin(p)
        bp = plugin.setup(servers, payloads)
        if bp:
            app.register_blueprint(bp)

    return servers, payloads


def main():
    global mole_config
    servers = dict()
    payloads = dict()
    load_plugins(servers, payloads)

    log.info('Loaded ' + str(len(payloads.keys())) + ' payloads')
    log.info('Loaded ' + str(len(servers.keys())) + ' servers')

    # check python version
    if not float(sys.version[0:3]) >= 3.6:
        log.critical('Mole requires Python 3.6 or later')
        sys.exit()

    # Dynamically build the menu based on the plugins
    ap = argparse.ArgumentParser()
    ap.add_argument('--all', '-a', action='store_true', help='Generate all payloads')
    ap.add_argument('--config', '-c', type=str, help='Configuration file', default='config.yml')
    ap.add_argument('--debug', '-d', action='store_true', help='Debug messages')
    ap.add_argument('--length', '-l', type=int, help='Override the token length in the config file', default=None)
    ap.add_argument('--numtokens', '-n', type=int, help='Number of raw tokens to generate', default=10)
    ap.add_argument('--output', '-o', type=str, help='Output directory', default='output')
    ap.add_argument('--raw', '-r', action='store_true', help='Print raw tokens')
    ap.add_argument('--server', '-s', action='store_true', help='Run the Mole server')
    ap.add_argument('--tags', '-t', type=str, help='Comma separated tags to a payload such as a client name',
                    default=None)

    for p in payloads.keys():
        ap.add_argument('--%s' % p,  action='store_true', help=payloads[p].description)

    args = ap.parse_args()
    try:
        mole_config = Config(args.config)
        mole_config.output = args.output
    except FileNotFoundError:
        exit('Configuration file %s not found' % args.config)

    if args.debug:
        log.setLevel(logging.DEBUG)
        mole_config.debug = True

    if args.server:
        if __name__ == '__main__':
            # Load the notification plugins
            plugin_dirs = get_plugin_dirs('notifications')
            plugin_base = PluginBase(package='mole.plugins')
            plugin_source = plugin_base.make_plugin_source(searchpath=plugin_dirs)
            log.debug('Plugin dirs: ' + ", ".join(plugin_dirs))
            log.debug(plugin_dirs)

            notifications = list()
            for p in plugin_source.list_plugins():
                log.debug('Loading plugin: ' + p)

                plugin = plugin_source.load_plugin(p)
                n = plugin.setup()
                _n = n(config=mole_config)
                if _n.isEnabled():
                    notifications.append(_n)

            log.debug(notifications)
            mole_config.notifications = notifications
            app.config['API_KEY'] = mole_config.server_api_key
            app.config['mole_config'] = mole_config
            launch(mole_config, app)
    else:
        if args.length:
            mole_config.token_length = args.length

        if args.tags is not None:
            mole_config.tags = mole_config.tags + args.tags.split(',')

        if not token_server_health_check(mole_config):
            log.critical('Unable to connect to mole server %s' % mole_config.token_server)
            sys.exit()
        else:
            log.info('Successfully connected to mole server ' + mole_config.token_server)

        if args.raw:
            for i in range(0, args.numtokens):
                #print('mole_config.tags: ' + ','.join(mole_config.tags))
                tags = deepcopy(mole_config.tags)
                tags.append('raw%i' % i)
                log.debug('tags' + ','.join(tags))
                #print('tags: ' + ','.join(tags))
                t = TrackingToken(config=mole_config, tags=tags)

                print(t.full_token())

        plugin_dirs = get_plugin_dirs(path='payloads')
        plugin_base = PluginBase(package='mole.plugins')
        plugin_source = plugin_base.make_plugin_source(searchpath=plugin_dirs)
        log.debug('Plugin dirs: ' + ", ".join(plugin_dirs))
        log.debug(plugin_dirs)

        payloads = dict()
        for p in plugin_source.list_plugins():
            log.debug('Loading plugin: ' + p)

            plugin = plugin_source.load_plugin(p)
            _ = plugin.setup(servers, payloads)
            if payloads.get(p, None):
                log.debug(payloads[p])
                log.debug(type(payloads[p]))
                p = payloads[p](config=mole_config)
                log.debug(type(p))
                #p.build()
            #:w
            # :w
            # payloads[p] = p

        ad = args.__dict__
        log.debug('args dict: ' + str(ad))
        log.debug('payloads: ' + str(payloads))
        """
        for arg in ad.keys():
            if ad[arg] is True and payloads.get(arg, None):
                log.info('Executing ' + arg)
                # run payload
                print(globals())
                print("*" * 80)
                print(payloads[arg].__dict__)
                clsname = ".".join([payloads[arg].__module__, payloads[arg].__name__])
                print(type(clsname, (), {}))
                print(isinstance(payloads[arg], ListPluginMixin))
                print('b' + str(payloads[arg].__module__))
                #ListPluginMixin.__module__
                print(type(payloads[arg]))
                clsname = ".".join([payloads[arg].__module__, payloads[arg].__name__])
                print(payloads[arg])
                print('clsname: ' + clsname)
        """

        for arg in ad.keys():
            if ad[arg] is True and payloads.get(arg, None) or ad['all'] == True and payloads.get(arg, None):
                log.info('Executing ' + arg)
                # run payload
                log.debug(payloads[arg].__dict__)
                payload = payloads[arg](config=mole_config)
                res = payload.build()
                if not os.path.isdir(args.output):
                    os.mkdir(args.output)

                output_file = os.path.join(args.output, "%s.txt" % arg)
                if isinstance(payload, ListPluginMixin):
                    print("Writing %i %s payloads to %s" % (len(res), arg, output_file))
                    with open(output_file, 'w') as fout:
                        for line in res:
                            fout.write(line + "\n")

        """
        if args.all:
            res = build_all_payloads(payloads)
            for r in res:
                print(r)
        """


def build_all_payloads(payloads):
    all = list()
    for p in payloads.keys():
        payload = payloads[p](config=mole_config)
        res = payload.build()
        for r in res:
            all.append(r)

    return all


if __name__ == '__main__':
    try:
        main()
    except requests.ConnectionError:
        log.error("Unable to connect to token server.")
