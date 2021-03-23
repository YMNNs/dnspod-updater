import os
import re
import sys
import requests
import json
import time

GET_DOMAIN_LIST_URL = ''
GET_RECORD_LIST_URL = ''
GET_QUALIFIED_RECORD_TYPE_URL = ''
MODIFY_RECORD_URL = ''
GET_IPV4_METHOD = 'request'
GET_IPV6_METHOD = 'request'
GET_IPV6_REQUEST_URL = ''
GET_IPV4_REQUEST_URL = ''
GET_IPV6_COMMAND = ''
GET_IPV4_COMMAND = ''
REGEX_IPV6 = '(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))'
REGEX_IPV4 = '(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}'
IPV4 = ''
IPV6 = ''
CLOSE_TIMEOUT = 5


def exit_after_countdown():
    log('INFO', '程序将在{}秒后退出'.format(CLOSE_TIMEOUT))
    time.sleep(CLOSE_TIMEOUT)
    sys.exit(0)

def get_windows_ipv6_address():
    output = os.popen("ipconfig /all").read()
    result = re.findall(r"(([a-f0-9]{1,4}:){7}[a-f0-9]{1,4})", output, re.I)
    return result[0][0]


def get_ipv4_command(command):
    ipv4 = os.popen(command).read()
    if re.match(REGEX_IPV4, ipv4):
        return ipv4
    else:
        log('WARN', '无效IPV4地址')
        raise ValueError('无效IPV4地址')


def get_ipv6_command(command):
    ipv6 = os.popen(command).read()
    ipv6 = re.findall(r"(([a-f0-9]{1,4}:){7}[a-f0-9]{1,4})", ipv6, re.I)[0][0]
    if re.match(REGEX_IPV6, ipv6):
        return ipv6
    else:
        log('WARN', '无效IPV6地址')
        raise ValueError('无效IPV6地址')


def get_ipv6_request(url):
    response = requests.get(url)
    if response.status_code == 200:
        if re.match(REGEX_IPV6, response.text):
            return response.text
        else:
            log('WARN', '无效IPV6地址')
            raise ValueError('无效IPV6地址')
    else:
        log('WARN', '连接API失败')
        raise ConnectionError('连接API失败')


def get_ipv4_request(url):
    response = requests.get(url)
    if response.status_code == 200:
        if re.match(REGEX_IPV4, response.text):
            return response.text
        else:
            log('WARN', '无效IPV4地址')
            raise ValueError('无效IPV4地址')
    else:
        log('WARN', '连接API失败')
        raise ConnectionError('连接API失败')


def update_ip():
    global IPV4
    print('IPv4: pending', end='\r')
    if GET_IPV4_METHOD.lower() == 'command':
        try:
            IPV4 = get_ipv4_command(GET_IPV4_COMMAND)
            print('IPv4: {}'.format(IPV4), flush=True)
        except Exception:
            IPV4 = ''
            log('WARN', '无法通过系统命令获取IPv4地址')
    else:
        try:
            IPV4 = get_ipv4_request(GET_IPV4_REQUEST_URL)
            print('IPv4: {}'.format(IPV4), flush=True)
        except Exception:
            IPV4 = ''
            log('WARN', '无法通过网络请求获取IPv4地址')
    global IPV6
    print('IPv6: pending', end='\r')
    if GET_IPV6_METHOD.lower() == 'command':
        try:
            IPV6 = get_ipv6_command(GET_IPV6_COMMAND)
            print('IPv6: {}'.format(IPV6), flush=True)
        except Exception:
            IPV6 = ''
            log('WARN', '无法通过系统命令获取IPv6地址')
    else:
        try:
            IPV6 = get_ipv6_request(GET_IPV6_REQUEST_URL)
            log('INFO', '如果您的计算机启用了临时（隐私）IPv6地址，获取的地址可能无法被其他计算机连接。')
            print('IPv6: {}'.format(IPV6), flush=True)
        except Exception:
            IPV6 = ''
            log('WARN', '无法通过网络请求获取IPv6地址')


class Record:
    domain_grade: str
    domain_id: str
    id: str
    name: str
    sub_domain: str
    record_type: str
    value: str


def load_domains():
    with open('domains.json', 'r') as f:
        config = json.load(f)
    headers = config.get('headers')
    params = config.get('params')
    domains = config.get('domains')
    records = []
    for domain in domains:
        record = Record()
        record.name = domain.get('name')
        record.sub_domain = domain.get('sub_domain')
        record.record_type = domain.get('record_type')
        record.value = domain.get('value')
        records.append(record)
    domains = records
    return headers, params, domains


def load_config():
    with open('config.json', 'r') as f:
        config = json.load(f)
        global GET_DOMAIN_LIST_URL
        GET_DOMAIN_LIST_URL = config.get('get_domain_list_url')
        global GET_RECORD_LIST_URL
        GET_RECORD_LIST_URL = config.get('get_record_list_url')
        global GET_QUALIFIED_RECORD_TYPE_URL
        GET_QUALIFIED_RECORD_TYPE_URL = config.get('get_qualified_record_type_url')
        global MODIFY_RECORD_URL
        MODIFY_RECORD_URL = config.get('modify_record_url')
        global GET_IPV6_METHOD
        GET_IPV6_METHOD = config.get('get_ipv6_method')
        if GET_IPV6_METHOD.lower() == 'request':
            global GET_IPV6_REQUEST_URL
            GET_IPV6_REQUEST_URL = config.get('get_ipv6_request_url')
        else:
            GET_IPV6_METHOD = 'command'
            global GET_IPV6_COMMAND
            GET_IPV6_COMMAND = config.get('get_ipv6_command')
        global GET_IPV4_METHOD
        GET_IPV4_METHOD = config.get('get_ipv4_method')
        if GET_IPV4_METHOD.lower() == 'request':
            global GET_IPV4_REQUEST_URL
            GET_IPV4_REQUEST_URL = config.get('get_ipv4_request_url')
        else:
            GET_IPV4_METHOD = 'command'
            global GET_IPV4_COMMAND
            GET_IPV4_COMMAND = config.get('get_ipv4_command')
        global CLOSE_TIMEOUT
        CLOSE_TIMEOUT = config.get('close_timeout')


def get_domain_list(headers, params):
    return send_post(GET_DOMAIN_LIST_URL, headers, params).get('domains')


def get_domain_info(name, domain_list):
    for domain in domain_list:
        if domain.get('name').lower() == name.lower():
            return domain
    log('WARN', '未找到域名{}'.format(name))
    raise NameError('未找到域名{}'.format(name))


def get_record_list(domain_id, headers, params):
    params.update({'domain_id': domain_id})
    return send_post(GET_RECORD_LIST_URL, headers, params).get('records')


def get_record_info(record_list, sub_domain):
    for record in record_list:
        if record.get('name').lower() == sub_domain.lower():
            return record
    log('WARN', '未找到记录{}'.format(sub_domain))
    raise NameError('未找到记录{}'.format(sub_domain))


def get_qualified_record_type(domain_grade, headers, params):
    params.update({'domain_grade': domain_grade})
    return send_post(GET_QUALIFIED_RECORD_TYPE_URL, headers, params).get('types')


def modify_record(domain_id, record_id, sub_domain, record_type, record_line, value, mx, headers, params):
    params.update({'domain_id': domain_id, 'record_id': record_id, 'sub_domain': sub_domain, 'record_type': record_type,
                   'record_line': record_line, 'value': value, 'mx': mx, })
    return send_post(MODIFY_RECORD_URL, headers, params)


def send_post(url, headers, params):
    response = requests.post(url, data=params, headers=headers)
    if response.status_code == 200:
        response_dict = json.loads(response.text)
        if response_dict.get('status').get('code') == '1':
            return response_dict
        else:
            raise ValueError(
                '{} ({})'.format(response_dict.get('status').get('message'), response_dict.get('status').get('code')))
    else:
        log('ERROR', '连接API失败')
        raise ConnectionError('连接API失败')


def log(log_type, text):
    now = time.strftime("%a %b %d %H:%M:%S %Y", time.localtime())
    if log_type == 'INFO':
        tag = '\033[1;37;42m INFO \033[0m'
    elif log_type == 'WARN':
        tag = '\033[1;37;43m WARN \033[0m'
    elif log_type == 'ERROR':
        tag = '\033[1;37;41m ERROR \033[0m'
    else:
        tag = '\033[1;30;47m UNK \033[0m'
    print('{} {} {}'.format(now, tag, text))
