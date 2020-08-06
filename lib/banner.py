# -*- coding: utf-8 -*-
from .util import get_version


def banner():

    logo = """

 ███▄ ▄███▓ ▒█████   ██▓    ▓█████ 
▓██▒▀█▀ ██▒▒██▒  ██▒▓██▒    ▓█   ▀ 
▓██    ▓██░▒██░  ██▒▒██░    ▒███   
▒██    ▒██ ▒██   ██░▒██░    ▒▓█  ▄ 
▒██▒   ░██▒░ ████▓▒░░██████▒░▒████▒
░ ▒░   ░  ░░ ▒░▒░▒░ ░ ▒░▓  ░░░ ▒░ ░
░  ░      ░  ░ ▒ ▒░ ░ ░ ▒  ░ ░ ░  ░
░      ░   ░ ░ ░ ▒    ░ ░      ░   
       ░       ░ ░      ░  ░   ░  ░
                                   
v{0}
Out of Band Payload Framework
Black Hat Arsenal 2020 Edition
""".format(get_version())
    print(logo)
