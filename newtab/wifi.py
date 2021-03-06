import base64
import json
import os
import socket
import subprocess
import sys
import time
import uuid

import requests

import newtab


_config_file = os.path.join(newtab.app.instance_path, 'wifi.json')
if not os.path.isfile(_config_file):
    raise FileNotFoundError('instance/wifi.json not found')

with open(_config_file, encoding='utf-8') as _file:
    _config = json.load(_file)

_user_config_file = os.path.join(newtab.app.instance_path, 'wifi-user.json')
if os.path.isfile(_user_config_file):
    with open(_user_config_file, encoding='utf-8') as _file:
        _config.update(json.load(_file))


def google_connectivity(timeout=5):
    try:
        response = requests.head('http://google.com', timeout=timeout)
    except requests.RequestException:
        return False
    else:
        return response.elapsed.total_seconds()


def baidu_connectivity(timeout=5):
    try:
        response = requests.head('http://baidu.com', timeout=timeout)
    except requests.RequestException:
        return False
    else:
        return response.elapsed.total_seconds()


def ip():
    return socket.gethostbyname(hostname())


def hostname():
    return socket.gethostname()


def mac():
    return ':'.join(f'{byte:02x}'
                    for byte in uuid.getnode().to_bytes(6, 'big'))


def wifi():
    if sys.platform != 'darwin':
        return _config['ssid']  # TODO
    commands = ['networksetup', '-getairportnetwork', 'en0']
    output = subprocess.check_output(commands, shell=False).decode()
    if output.startswith('You are not associated with an AirPort network.\n'):
        return False
    return output.split()[-1]


def login():
    if wifi() != _config['ssid']:
        return False

    password = base64.b64decode(_config['password']).decode()
    rckey = str(int(time.time() * 1000))
    pwd = _do_encrypt_rc4(password, rckey)
    params = {
        'opr': 'pwdLogin',
        'userName': _config['username'],
        'pwd': pwd,
        'rc4Key': rckey,
        'rememberPwd': '1'
    }

    try:
        response = requests.post(_config['login_url'], data=params)
    except requests.RequestException:
        return False

    response.encoding = 'utf-8'
    status = json.loads(response.text.replace("'", '"'))
    logged_in = status.get('msg') == _config['logged_in_message']
    return status.get('success') or logged_in


def _do_encrypt_rc4(source, raw_key):
    # Literal line-by-line translation of the original do_encrypt_rc4
    # JavaScript function of the login page
    source = source.strip()

    key = []
    sbox = []
    for i in range(256):
        key.append(ord(raw_key[i % len(raw_key)]))
        sbox.append(i)

    j = 0
    for i in range(256):
        j = (j + sbox[i] + key[i]) % 256
        sbox[i], sbox[j] = sbox[j], sbox[i]

    output = []
    a = b = c = 0
    for i in range(len(source)):
        a = (a + 1) % 256
        b = (b + sbox[a]) % 256
        sbox[a], sbox[b] = sbox[b], sbox[a]
        c = (sbox[a] + sbox[b]) % 256
        out = ord(source[i]) ^ sbox[c]
        out = hex(out).lstrip('0x').rjust(2, '0')
        output.append(out)

    return ''.join(output)
