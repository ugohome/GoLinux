# -*- coding:utf-8 -*-

import re, os
from flask import request, render_template, redirect, send_from_directory
import urllib.request
from raid.meth import get_cmd_value
from DRS.share import get_svr_info

def index():
    try:
        svrs = [
            'drs-admin', 'drs-api', 'drs-solr', 'drs-transcode', 'pgsql', 'nginx',
            'solr', 'redis', 'rabbitmq', 'proftpd', 'oo'
                    ]
        url_svr_name = ['drs-admin', 'drs-api']
        svr_table = []
        ssl_model = get_cmd_value("sed -n '/#.*ssl on;/p' /drsBT/nginx/conf/nginx.conf")
        if ssl_model:
            ssl = 'http'
        else:
            ssl = 'https'
            #return render_template('test.html', t1=ssl_model)
        ssl_d = {}
        ssl_d['ssl'] = ssl
        for svr in svrs:
            svr_table.append(get_svr_info(svr))

        #通过端口号判断服务是否真正启动完成,并重写svr_table
        ng_port_cmd = get_cmd_value("grep 'mvport' /drsBT/nginx/conf/nginx.conf |awk '{print($3)}'")
        proftp_port_cmd = get_cmd_value("grep 'mvport' /drsBT/proftpd/etc/proftpd.conf |awk '{print($3)}'")
        ng_port = ng_port_cmd[0][0]
        proftp_port = proftp_port_cmd[0][0]
        svr_ports = {
            'drs-admin': '8888',
            'drs-api': '8885',
            'drs-solr': '8887',
            'drs-transcode': '8889',
            'pgsql': '5432',
            'nginx': str(ng_port),
            'solr': '8983',
            'redis': '6379',
            'rabbitmq': '5672',
            'proftpd': str(proftp_port),
            'oo': '8100'
        }
        for svr in svr_table:
            if re.match(r'^active', svr['svr_state']):
                listen_port_cmd = "netstat -lanp|grep :"+svr_ports[svr['svr_name']]+".*LISTEN"
                listen_port = get_cmd_value(listen_port_cmd)
                if listen_port[0][0] == 'ERROR':
                    svr['svr_state'] = 'active(starting)'
                else:
                    svr['svr_state'] = 'active(OK)'


        #重写admin,api,solr,transcode,nginx状态信息,只有URL可正常访问才算成功.
        for i, line in enumerate(svr_table):
            url = 'http://127.0.0.1:'
            if line['svr_name'] == 'drs-admin':
                url = url+'8888/drs-admin/'
            if line['svr_name'] == 'drs-api':
                url = url+'8885/drs-api/'
            '''
            if line['svr_name'] == 'drs-solr':
                url = url+'8887/drs-solr/'
            if line['svr_name'] == 'drs-transcode':
                url = url+'8889/drs-transcode/'
            
            if line['svr_name'] == 'nginx':
                if ssl == 'http':
                    url = url+'8088/'
                if ssl == 'https':
                    url = 'https://127.0.0.1:8088/'
            '''
            if line['svr_name'] in url_svr_name:
                try:
                    urllib.request.urlopen(url)
                    svr_table[i]['svr_state'] = 'active(OK)'
                except Exception:
                    if line['svr_state'][0:6] == 'active':
                        svr_table[i]['svr_state'] = 'active(starting)'

        #获取一次请求的所有参数值,如下样式:
        # [('svr_state', 'failed(Result:'), ('svr_name', 'drs-admin')]), ImmutableMultiDict([])]
        reqs = request.values
        if reqs:
            for req in reqs:
                if req == 'svr_state':
                    svr_state = reqs[req]
                if req == 'svr_name':
                    svr_name = reqs[req]
                if req == 'svr_auto':
                    svr_auto = reqs[req]
                if req == 'log_name':
                    log_name = reqs[req]
                if req == 'mod_port':
                    mod_port = reqs[req]
                if req == 'ssl_model':
                    get_ssl = reqs[req]

            #判断一个变量是否已经定义 'val' in dir()
            if 'svr_state' in dir() and svr_state[0:6] == 'active':
                get_cmd_value('systemctl stop ' + svr_name)
            if 'svr_state' in dir() and svr_state[0:6] != 'active':
                get_cmd_value('systemctl start ' + svr_name)
            if 'svr_auto' in dir() and svr_auto == 'disabled':
                get_cmd_value('systemctl enable ' + svr_name)
            if 'svr_auto' in dir() and svr_auto == 'enabled':
                get_cmd_value('systemctl disable ' + svr_name)
            #生成日志下载
            if 'log_name' in dir():
                if log_name == 'drs-admin':
                    return send_from_directory('/drsBT/log/', 'drs-admin.log', as_attachment=True)
                if log_name == 'drs-api':
                    return send_from_directory('/drsBT/log/', 'drs-api.log', as_attachment=True)
                if log_name == 'drs-solr':
                    return send_from_directory('/drsBT/log/', 'drs-solr.log', as_attachment=True)
                if log_name == 'drs-transcode':
                    return send_from_directory('/drsBT/log/', 'drs-transcode.log', as_attachment=True)
            #修改NGINX及PROFTPD端口号
            if 'mod_port' in dir():
                if svr_name == 'nginx':
                    etc_path = '/drsBT/nginx/conf/nginx.conf'
                if svr_name == 'proftpd':
                    etc_path = '/drsBT/proftpd/etc/proftpd.conf'
                old_port_cmd = "grep 'mvport' "+etc_path+" |awk '{print($3)}'"
                old_port = get_cmd_value(old_port_cmd)
                mod_port_cmd = "sed -i 's/"+old_port[0][0]+"/"+mod_port+"/g' "+etc_path
                get_cmd_value(mod_port_cmd)
                get_cmd_value('systemctl stop '+svr_name)
                get_cmd_value('systemctl start ' + svr_name)
            #http与https模式切换
            if 'get_ssl' in dir():
                if get_ssl == 'http':
                    get_cmd_value("sed -i 's/#.*ssl on;/ssl on;/' /drsBT/nginx/conf/nginx.conf")
                    get_cmd_value("sed -i 's/ws:\/\//wss:\/\//' /drsBT/drs/drs-web/drs-web/script/common.js")
                if get_ssl == 'https':
                    get_cmd_value("sed -i 's/.*ssl on;/#ssl on;/' /drsBT/nginx/conf/nginx.conf")
                    get_cmd_value("sed -i 's/wss:\/\//ws:\/\//' /drsBT/drs/drs-web/drs-web/script/common.js")
                get_cmd_value("systemctl stop nginx")
                get_cmd_value("systemctl start nginx")
            return redirect('/drs/')
        return render_template('drs.html', svr_table=svr_table, ssl_d=ssl_d, svr_ports=svr_ports)
    except:
        return render_template('drs.html')
def update():
    '''
    前端上传完包及SH角本,点击开始执行按钮,
    后端执行完成后返回日志下载.
    '''
    now_path = os.path.abspath(os.path.dirname(__file__)) #获取当前路径'/pyst/PTL/DRS/'
    base_path = os.path.dirname(now_path) # 获取父目录'/pyst/PTL/'
    update_path = os.path.join(base_path, 'update/')
    f = request.files.get('file')
    update = request.form.get('update')
    log_name = request.args.get('log_name')
    if log_name:
        return send_from_directory(update_path, log_name, as_attachment=True)
    if f:
        f.save(update_path+f.filename)
        #return render_template('test.html', t2=f.filename)
    if update:
        logs = []
        get_cmd_value('rm -rf '+update_path+'*.log')
        get_cmd_value('chmod 755 '+update_path+'*')
        for file in os.listdir(update_path):
            f = os.path.splitext(update_path+file)
            if f[1] == '.sh':  #文件类型一定要加"."(.sh)
                os.chdir(update_path)  #改前工作路径为update目录,让.sh文件生成日志存放update目录下.
                get_cmd_value(update_path+file)
                #logs.append(update_path+file)
        #执行完sh文件后可能产生log文件,需要重新再遍历一次目录生成logs列表.保留log文件并删除其余文件.
        for file in os.listdir(update_path):
            f = os.path.splitext(update_path + file)
            if f[1] == '.log':
                logs.append(file)
            else:
                get_cmd_value('rm -rf '+update_path+file)
                #logs.append(update_path+file)

        if len(logs) == 0: #如果没有.log文件,生成空列表,这样前端就能获取到一个空列表,否则前端无法获取到列表.
            logs.append('')

        #return render_template('test.html', t1=logs, t2=file)
        return render_template('update.html', logs=logs)
    return render_template('update.html')