# -*- coding: utf-8 -*-

import psutil, os, time, multiprocessing, datetime
from flask import render_template,request, redirect
from raid.meth import get_cmd_value
from system.share import get_hum_data, get_proc_info

def index():
    if request.method == 'POST':
        mod_dt = request.form.get('dt')
        get_cmd_value('date -s "'+mod_dt+'"')
        get_cmd_value('clock -w')
        get_cmd_value('rm -rf /etc/localtime')
        get_cmd_value('\cp -rf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime')
    dt = datetime.datetime.today()
    syscmd = request.args.get('syscmd')
    kill_pid = request.args.get('kill_pid')
    if syscmd and syscmd == 'reboot':
        try:
            return '<div style="color: midnightblue"><h4>正在重启服务器......</h4></div>'
        finally:
            #pass
            get_cmd_value('reboot')
    if syscmd and syscmd == 'poweroff':
        try:
            return '<div style="color: midnightblue"><h4>正在关闭服务器......</h4></div>'
        finally:
            pass
            #get_cmd_value('poweroff')
    if kill_pid:
        get_cmd_value('kill -9 '+kill_pid)
        return redirect('/system/process/')
    sysinfo = {}
    MAC = get_cmd_value("ifconfig |grep ether |head -1|awk '{print($2)}'")
    sysinfo['MAC'] = MAC[0][0]
    cpu_info = psutil.cpu_times_percent()
    sysinfo['cpu_loadavg'] = psutil.getloadavg()
    sysinfo['cpu_user'] = cpu_info.user
    sysinfo['cpu_system'] = cpu_info.system
    sysinfo['cpu_iowait'] = cpu_info.iowait
    sysinfo['cpu_other'] = cpu_info.nice+cpu_info.irq+cpu_info.softirq+cpu_info.steal+cpu_info.guest+cpu_info.guest_nice
    sysinfo['cpu_idle'] = cpu_info.idle
    sysinfo['cpu_count_logical'] = psutil.cpu_count(logical=True)
    #cpu核芯数,如:双核(2)
    sysinfo['cpu_count_phy'] = psutil.cpu_count(logical=False)
    #cpu线程数,如:4线程(4)
    cpu_type_cmd = get_cmd_value("cat /proc/cpuinfo |grep 'model name'|head -1|awk -F : '{print($2)}'")
    cpu_type = ''
    for i in cpu_type_cmd[0]:
        cpu_type = cpu_type+i+' '
    sysinfo['cpu_type'] = cpu_type

    mem = psutil.virtual_memory()
    sysinfo['mem_total'] = get_hum_data(mem.total)
    sysinfo['mem_used'] = get_hum_data(mem.used)
    sysinfo['mem_percent'] = mem.percent
    sysinfo['mem_free'] = get_hum_data(mem.free)
    sysinfo['mem_buff_cache'] = get_hum_data(mem.buffers+mem.cached)

    swap = psutil.swap_memory()
    sysinfo['swap_total'] = get_hum_data(swap.total)
    sysinfo['swap_used'] = get_hum_data(swap.used)
    sysinfo['swap_percent'] = swap.percent
    sysinfo['swap_free'] = get_hum_data(swap.free)

    io_r1 = psutil.disk_io_counters().read_bytes
    io_w1 = psutil.disk_io_counters().write_bytes
    net_sent1 = psutil.net_io_counters().bytes_sent
    net_recv1 = psutil.net_io_counters().bytes_recv
    time.sleep(1)
    io_r2 = psutil.disk_io_counters().read_bytes
    io_w2 = psutil.disk_io_counters().write_bytes
    net_sent2 = psutil.net_io_counters().bytes_sent
    net_recv2 = psutil.net_io_counters().bytes_recv
    io_r = get_hum_data(io_r2-io_r1)
    io_w = get_hum_data(io_w2-io_w1)
    net_sent = get_hum_data(net_sent2 - net_sent1)
    net_recv = get_hum_data(net_recv2 - net_recv1)
    sysinfo['io_read'] = io_r
    sysinfo['io_write'] = io_w
    sysinfo['net_sent'] = net_sent
    sysinfo['net_recv'] = net_recv
    sysinfo['dt'] = dt
    return render_template('system.html', sysinfo=sysinfo)

def process():
    manage = multiprocessing.Manager()
    #with multiprocessing.Manager() as manage:
    process_info = manage.list()

    ps = []
    for pid in psutil.pids():
        p = multiprocessing.Process(target=get_proc_info, args=(process_info, pid,))
        #manage.list()列表必需传到函数里,并在函数里进行列表内容填加
        p.daemon = True
        ps.append(p)

    for p in ps:
        p.start()
    for p in ps:
        p.join()

    #本系统自身及其子进程PID列表
    myself_pid = []
    my_proc = psutil.Process()
    myself_pid.append(my_proc.pid)
    myself_pid.append(my_proc.ppid())
    for child_proc in my_proc.children():
        myself_pid.append(child_proc.pid)

    #cpu,mem前10 pid字典
    cpu_per = {}
    #{2246: 7.3, 2242: 2.0,....}
    mem_per = {}
    for proc in process_info:
        #不包含自身的PID
        if proc['pid'] not in myself_pid:
            cpu_per[proc['pid']] = proc['cpu_percent']
            mem_per[proc['pid']] = proc['mem_percent']
    cpu_per_top = sorted(cpu_per.items(), key=lambda v: v[1], reverse=True)[0:10]
    #[(2246, 7.3), (2242, 2.0), (28551, 1.7), ......]
    #字典排序,key遍历cpu_per.items()值为v[1]
    mem_per_top = sorted(mem_per.items(), key=lambda v: v[1], reverse=True)[0:10]

    cpu_top_info = []
    for cpu in cpu_per_top:
        for p in process_info:
            if cpu[0] == p['pid']:
                cpu_top_info.append(p)

    mem_top_info = []
    for mem in mem_per_top:
        for m in process_info:
            if mem[0] == m['pid']:
                mem_top_info.append(m)

    #return render_template('test.html', t1=cpu_top_info, t2=myself_pid)
    return render_template('process.html', cpu_top=cpu_top_info, mem_top=mem_top_info)