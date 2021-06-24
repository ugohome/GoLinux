# -*- coding: utf-8 -*-

import psutil

def get_hum_data(data, *unit):
    # B K M G T
    ud = {'B':1, 'K':2, 'M':3, 'G':4, 'T':5}
    for i in range(1, 6):
        unit_name = [u for u in ud if ud[u] == i+1]
        if round(data, 2) < 1024:
            hum_data = str(round(data, 2))+' B'
        if round(data, 2) >= pow(1024, i):
            hum_data = str(round(data/pow(1024, i)))+' '+unit_name[0]
    return hum_data

def get_proc_info(cpu_list, pid):
    info = {}
    p = psutil.Process(pid)
    info['pid'] = pid
    info['ppid'] = p.ppid()
    cmd = ''
    for i in p.cmdline():
        cmd = cmd+' '+i
    info['cmd'] = cmd
    info['cpu_percent'] = round(p.cpu_percent(interval=2), 2)
    #获取cpu_percent必需加interval秒数,否则取到的都为0
    info['mem_rss'] = get_hum_data(p.memory_info().rss)
    info['mem_percent'] = round(p.memory_percent(), 2)
    cpu_list.append(info)
    #return info
