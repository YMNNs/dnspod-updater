import util
import os
import time


def main():
    os.system('')
    print('\033[1;37;44m {} \033[0m\n'.format(util.VERSION))
    try:
        util.load_config()
    except Exception as e:
        util.log('ERROR', '文件config.json不存在或可能已经损坏')
        exit(0)
    while True:
        if util.SERVICE:
            util.log('INFO', '开始运行定时任务，间隔{}秒'.format(util.CHECK_INTERVAL))
            run_once()
            util.log('INFO', '下次任务将开始于{}'.format(
                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + util.CHECK_INTERVAL))))
            time.sleep(util.CHECK_INTERVAL)
        else:
            run_once()
            break


def run_once():
    try:
        headers, params, domains = util.load_domains()
    except Exception as e:
        util.log('ERROR', '文件domains.json不存在或可能已经损坏')
        util.exit_after_countdown()
        return
    util.update_ip()
    try:
        domain_list = util.get_domain_list(headers, params)
    except Exception as e:
        util.log('ERROR', e)
        util.exit_after_countdown()
        return
    success = []
    fail = []
    for d in domains:
        try:
            util.log('INFO', '正在更新{}'.format(util.sub_domain_and_domain(d.sub_domain, d.name)))
            domain = util.get_domain_info(d.name, domain_list)
            qualified_record_types = util.get_qualified_record_type(domain.get('grade'), headers, params)
            if d.record_type not in qualified_record_types:
                fail.append({'name': util.sub_domain_and_domain(d.sub_domain, d.name), 'type': d.record_type})
                util.log('ERROR', '记录类型{}不在可用类型{}中'.format(d.record_type, qualified_record_types))
                continue
            record_list = util.get_record_list(domain.get('id'), headers, params)
            record = util.get_record_info(record_list, d.sub_domain, d.record_type)
            domain_id = domain.get('id')
            record_id = record.get('id')
            sub_domain = d.sub_domain
            record_type = d.record_type
            record_line = record.get('line')
            if d.value == '$local_ipv6':
                if util.IPV6 == '':
                    util.log('WARN', '无有效的本机IPv6地址，跳过')
                    fail.append({'name': util.sub_domain_and_domain(d.sub_domain, d.name), 'type': d.record_type})
                    continue
                value = util.IPV6
            elif d.value == '$local_ipv4':
                if util.IPV4 == '':
                    util.log('WARN', '无有效的本机IPv4地址，跳过')
                    fail.append({'name': util.sub_domain_and_domain(d.sub_domain, d.name), 'type': d.record_type})
                    continue
                value = util.IPV4
            else:
                value = d.value
            if value == record.get('value'):
                util.log('INFO',
                         '域名{}当前的{}记录未发生改变'.format(util.sub_domain_and_domain(d.sub_domain, d.name), d.record_type))
                fail.append({'name': util.sub_domain_and_domain(d.sub_domain, d.name), 'type': d.record_type})
                continue
            mx = record.get('mx')
            util.modify_record(domain_id, record_id, sub_domain, record_type, record_line, value, mx,
                               headers,
                               params)
            success.append({'name': util.sub_domain_and_domain(d.sub_domain, d.name), 'type': d.record_type})
            util.log('INFO', '{}.{}的{}记录已更新为{}'.format(d.sub_domain, d.name, d.record_type, value))
        except Exception as e:
            util.log('ERROR', e)
            fail.append({'name': util.sub_domain_and_domain(d.sub_domain, d.name), 'type': d.record_type})
    if len(success) > 0:
        util.log('INFO', '\n\n 以下域名的DNS记录已成功更新:')
        for i in success:
            print('\t- {} ({})'.format(i.get('name'), i.get('type')))
        print()
    if len(fail) > 0:
        util.log('INFO', '\n\n 以下域名的DNS记录未被更改:')
        for i in fail:
            print('\t- {} ({})'.format(i.get('name'), i.get('type')))
        print()
    util.clear_ip()
    util.exit_after_countdown()
    return


if __name__ == '__main__':
    main()
