import dnspod
import os


def main():
    os.system('')
    print('\033[1;37;44m DNSPOD UPDATER 1.0.1 \033[0m\n')
    try:
        dnspod.load_config()
    except Exception as e:
        dnspod.log('ERROR', '文件config.json可能已经损坏')
        dnspod.exit_after_countdown()
    try:
        headers, params, domains = dnspod.load_domains()
    except Exception as e:
        dnspod.log('ERROR', '文件domains.json可能已经损坏')
        dnspod.exit_after_countdown()
    dnspod.update_ip()
    try:
        domain_list = dnspod.get_domain_list(headers, params)
    except Exception as e:
        dnspod.log('ERROR', e)
        dnspod.exit_after_countdown()
    success = []
    fail = []
    for d in domains:
        try:
            dnspod.log('INFO', '正在更新{}.{}'.format(d.sub_domain, d.name))
            domain = dnspod.get_domain_info(d.name, domain_list)
            qualified_record_types = dnspod.get_qualified_record_type(domain.get('grade'), headers, params)
            if d.record_type not in qualified_record_types:
                fail.append(d.sub_domain + '.' + d.name)
                dnspod.log('ERROR', '记录类型{}不在可用类型{}中'.format(d.record_type, qualified_record_types))
                continue
            record_list = dnspod.get_record_list(domain.get('id'), headers, params)
            record = dnspod.get_record_info(record_list, d.sub_domain)
            domain_id = domain.get('id')
            record_id = record.get('id')
            sub_domain = d.sub_domain
            record_type = d.record_type
            record_line = record.get('line')
            if d.value == '$local_ipv6':
                if dnspod.IPV6 == '':
                    dnspod.log('WARN', '无有效的本机IPv6地址，跳过')
                    fail.append(d.sub_domain + '.' + d.name)
                    continue
                d.value = dnspod.IPV6
                value = dnspod.IPV6
            elif d.value == '$local_ipv4':
                if dnspod.IPV4 == '':
                    dnspod.log('WARN', '无有效的本机IPv4地址，跳过')
                    fail.append(d.sub_domain + '.' + d.name)
                    continue
                d.value = dnspod.IPV4
                value = dnspod.IPV4
            else:
                value = d.value
            if d.value == record.get('value'):
                dnspod.log('INFO', '域名{}.{}当前的记录未发生改变'.format(sub_domain, d.name))
                fail.append(d.sub_domain + '.' + d.name)
                continue
            mx = record.get('mx')
            dnspod.modify_record(domain_id, record_id, sub_domain, record_type, record_line, value, mx,
                                 headers,
                                 params)
            success.append(d.sub_domain + '.' + d.name)
            dnspod.log('INFO', '{}.{}的{}记录已更新为{}'.format(d.sub_domain, d.name, d.record_type, d.value))
        except Exception as e:
            print(e)
            fail.append(d.sub_domain + '.' + d.name)
    if len(success) > 0:
        dnspod.log('INFO', '完成，\n\n 以下域名的DNS记录已成功更新:')
        for i in success:
            print('\t\t- {}'.format(i))
    if len(fail) > 0:
        dnspod.log('INFO', '完成，\n\n 以下域名的DNS记录未被更改:')
        for i in fail:
            print('\t - {}'.format(i))
    print()
    dnspod.exit_after_countdown()


if __name__ == '__main__':
    main()
