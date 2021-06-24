# -*- coding:utf-8 -*-

import re
from flask import request, render_template, redirect
from raid.meth import get_cmd_value
from net.share import dev_show, con_show, bond_show
import IPy
def index():
    bond_dev = []
    con_name = request.args.get('con_name')
    dev_name = request.args.get('dev_name')
    bond_link = request.args.get('bond_link')
    link = request.args.get('link')
    autocon = request.args.get('autocon')
    dev_info = dev_show()
    ips = IPy.IP('192.168.1.10/255.255.255.0', make_net=True)

    # 获取BOND所包含的所有网卡,用于前端过滤,只显示没有被BOND的网卡
    for dev in bond_show('yes'):
        bond_dev.append(dev['connection.interface-name:'])

    net_list = []
    for dev in dev_info:
        net_line = {}
        if dev['GENERAL.TYPE:'] == 'ethernet' and dev['GENERAL.DEVICE:'] not in bond_dev:
            net_line['dev_name'] = dev['GENERAL.DEVICE:']
            net_line['con_name'] = dev['GENERAL.CONNECTION:']
            net_line['type'] = dev['GENERAL.TYPE:']
            if '(connected)' in dev['GENERAL.STATE:'] or '连接' in dev['GENERAL.STATE:']:
                net_line['state'] = 'on'
                con_info = con_show(dev['GENERAL.CONNECTION:'])
                net_line['autocon'] = con_info['connection.autoconnect:']
                if con_info['connection.slave-type:'] == '--':
                    if con_info['ipv4.method:'] == 'auto':
                        dhcp_ip = con_info['DHCP4.OPTION[7]:'].split('=')

                        dhcp_mask_dict = {'netmask': con_info[i] for i in con_info if 'subnet_mask' in con_info[i]}
                        dhcp_mask = dhcp_mask_dict['netmask'].split('=')
                        gip = dhcp_ip[1] + '/' + dhcp_mask[1]
                        dhcp_gw_dict = {'gateway': con_info[i] for i in con_info if re.match(r'^routers.*', con_info[i])}
                        dhcp_gw = dhcp_gw_dict['gateway'].split('=')
                        '''
                        dhcp_mask = con_info['DHCP4.OPTION[28]:'].split('=')
                        gip = dhcp_ip[1]+'/'+dhcp_mask[1]
                        dhcp_gw = con_info['DHCP4.OPTION[27]:'].split('=')
                        '''
                        net_line['gateway'] = dhcp_gw[1]
                        dhcp_dns = con_info['DHCP4.OPTION[5]:'].split('=')
                        net_line['dns'] = dhcp_dns[1]
                        net_line['method'] = 'auto'
                    if con_info['ipv4.method:'] == 'manual':
                        gip = con_info['ipv4.addresses:']
                        net_line['gateway'] = con_info['ipv4.gateway:']
                        net_line['dns'] = con_info['ipv4.dns:']
                        net_line['method'] = 'manual'
                    ips = IPy.IP(gip, make_net=True)
                    net_line['ip'] = gip.split('/')[0]
                    net_line['netmask'] = ips.strNetmask()
            else:
                net_line['state'] = 'off'
            #if con_info['connection.slave-type:'] == '--':
            net_list.append(net_line)

    '''
    for devs in dev_info:
        dhcp_cmd = "nmcli con show '" + devs['GENERAL.CONNECTION:'] + "'|grep 'ipv4.method:'|awk '{print($2)}'"
        dhcp_value = get_cmd_value(dhcp_cmd)
        if len(dhcp_value) > 0:
            dhcp[devs['GENERAL.DEVICE:']] = dhcp_value[0][0]
            con_name[devs['GENERAL.DEVICE:']] = devs['GENERAL.CONNECTION:']
    '''
    if link == 'on':
        link_cmd = 'nmcli dev con '+dev_name
        get_cmd_value(link_cmd)
        return redirect('/net/')

    if link == 'off':
        link_cmd = 'nmcli dev discon '+dev_name
        get_cmd_value(link_cmd)
        return redirect('/net/')

    if bond_link == 'on':
        for dev in bond_dev:
            get_cmd_value('nmcli dev con '+dev)


    if bond_link == 'off':
        for dev in bond_dev:
            get_cmd_value('nmcli dev discon '+dev)


    if autocon == 'on':
        get_cmd_value('nmcli con mod "'+con_name+'" connection.autoconnect yes')
        return redirect('/net/')
        #return render_template('test.html', t1='nmcli con mod '+con_name+' connection.autoconnect yes')
    if autocon == 'off':
        get_cmd_value('nmcli con mod "'+con_name+'" connection.autoconnect no')
        return redirect('/net/')
        #return render_template('test.html', t1='nmcli con mod '+con_name+' connection.autoconnect no')

    #return render_template('test.html', t1=net_list, t2=dev_info)
    return render_template('net.html', netlist=net_list)

def net_mod():
    con_name = request.args.get('con_name')
    type = request.args.get('type')
    dns1 = request.form.get('dns1')
    dns2 = request.form.get('dns2')
    submit = request.form.get('submit')
    con_info = con_show(con_name)
    if 'IP4.ADDRESS[1]:' in con_info.keys():
        gip = con_info['IP4.ADDRESS[1]:']
        con_info['ip'] = gip.split('/')[0]
        ips = IPy.IP(gip, make_net=True)
        con_info['netmask'] = ips.strNetmask()

    if type == 'bond_del':
        #t = []
        for bond in bond_show('yes'):
            #t.append("nmcli con del '"+bond['connection.id:'])
            get_cmd_value("nmcli con del '"+bond['connection.id:']+"'")
        #return render_template('test.html', t1=t)
        return redirect('/net/net_bond/')

    if submit == '确定':
        method = request.form.get('method')
        dev_name = request.form.get('dev_name')
        con_name_fm = request.form.get('con_name')
        ip = request.form.get('ipv4')
        netmask = request.form.get('netmask')
        try:
            prefix = IPy.IP(ip + '/' + netmask, make_net=True).prefixlen()
            ipv4 = ip + '/' + str(prefix)
        except ValueError:
            return redirect('/net/net_bond/')
        gateway = request.form.get('gateway')

        mod_cmd_bs = "nmcli con mod '"+con_name_fm+"'"
        mod_cmd = mod_cmd_bs+" ipv4.method "+method+"  ipv4.addresses '"+ipv4+"' "
        get_cmd_value(mod_cmd)
        if gateway is None:
            mod_cmd_gw = mod_cmd_bs + " ipv4.gateway ''"
        else:
            mod_cmd_gw = mod_cmd_bs+" ipv4.gateway '"+gateway+"'"
        get_cmd_value(mod_cmd_gw)
        mod_cmd_dns_bs = ''
        mod_cmd_dns_null = ''
        mod_cmd_dns_nonull = ''
        if dns1 != '':
            mod_cmd_dns_bs = dns1+","
        if dns2 != '':
            mod_cmd_dns_bs = mod_cmd_dns_bs+dns2
        if dns1 == '' and dns2 == '':
            mod_cmd_dns_null = mod_cmd_bs+" ipv4.dns ''"
            get_cmd_value(mod_cmd_dns_null)
        else:
            mod_cmd_dns_nonull = mod_cmd_bs+" ipv4.dns '"+mod_cmd_dns_bs+"'"
            get_cmd_value(mod_cmd_dns_nonull)
        get_cmd_value("nmcli con down '"+con_name_fm+"'")
        get_cmd_value("nmcli con up '" + con_name_fm + "'")
        return redirect('/net/')
        #return render_template('test.html', test='gw-'+mod_cmd_gw, t1='null:'+mod_cmd_dns_null, t2='nonull:'+mod_cmd_dns_nonull)
    return render_template('net_mod.html', con_info=con_info)
    #return render_template('test.html', t1=con_info)

def net_bond():
    bonds = bond_show('yes')
    dev_name = request.form.getlist('dev_name')
    bond_type = request.form.get('bond_type')
    method = request.form.get('method')
    ipv4 = request.form.get('ipv4')
    netmask = request.form.get('netmask')
    gateway = request.form.get('gateway')
    dns = request.form.get('dns')
    submit = request.form.get('submit')
    if submit == '新建' and dev_name:
        if str(method) == 'manual':
            try:
                prefix = IPy.IP(ipv4 + '/' + netmask, make_net=True).prefixlen()
                ipv4 = ipv4 + '/' + str(prefix)
            except ValueError:
                return redirect('/net/net_bond/')
        bond_create_cmd = "nmcli con add con-name bond0 type bond ifname bond0 mode " + bond_type
        get_cmd_value(bond_create_cmd)
        get_method = "nmcli con mod bond0 ipv4.method '" + str(method) + "'"

        get_ip = "nmcli con mod bond0 ipv4.addresses '" + str(ipv4) + "'"
        get_gateway = "nmcli con mod bond0 ipv4.gateway '" + str(gateway) + "'"
        get_dns = "nmcli con mod bond0 ipv4.dns '" + str(dns) + "'"
        get_cmd_value(get_ip)
        get_cmd_value(get_gateway)
        get_cmd_value(get_dns)
        get_cmd_value(get_method)
        get_cmd_value("nmcli con up bond0")
        for dev in dev_name:
            slave_create_cmd = "nmcli con add con-name bond0-"+dev+" type bond-slave ifname "+dev+" master bond0"
            get_cmd_value(slave_create_cmd)
            get_cmd_value("nmcli con up bond0-"+dev)

        return redirect('/net/net_bond/')

    bond_list = []
    for bond in bonds:
        bond_line = {}
        bond_line['con_name'] = bond['connection.id:']
        bond_line['dev_name'] = bond['connection.interface-name:']
        bond_line['autocon'] = bond['connection.autoconnect:']
        if bond['connection.slave-type:'] == 'bond':
            bond_line['type'] = 'slave'
            state = get_cmd_value("nmcli dev show "+bond_line['dev_name']+"|grep 'WIRED-PROPERTIES.CARRIER:'")
            if state[0][1] == 'on' or '连接' in state[0][1]:
                bond_line['state'] = '连接'
            if state[0][1] == 'off':
                bond_line['state'] = '断开'
            #return render_template('test.html', t1=state)
        else:
            bond_line['type'] = 'bond'

            state = get_cmd_value("nmcli dev|grep '" + bond_line['dev_name'] + "'")
            '''
            state_dict = [i for i in bond_state_list if bond['connection.interface-name:'] in i.keys()]
            if state_dict:
                state = state_dict[0][bond['connection.interface-name:']]
            else:
                state = 'down'
            '''
            if state[0][0] == 'ERROR':
                bond_line['state'] = '断开'
            else:
                if state[0][2] == 'disconnected':
                #if state == 'down':
                    bond_line['state'] = '断开'
                if state[0][2] == 'connected' or '连接' in state[0][2]:
                #if state == 'up':
                    bond_line['state'] = '连接'
                    if bond['connection.slave-type:'] == '--':
                        if bond['ipv4.method:'] == 'auto':
                            bond_line['dhcp'] = '自动'
                            dhcp_ip = bond['DHCP4.OPTION[7]:'].split('=')
                            dhcp_mask_dict = {'netmask': bond[i] for i in bond if 'subnet_mask' in bond[i]}
                            dhcp_mask = dhcp_mask_dict['netmask'].split('=')
                            gip = dhcp_ip[1] + '/' + dhcp_mask[1]
                            dhcp_gw_dict = {'gateway': bond[i] for i in bond if re.match(r'^routers.*', bond[i])}
                            dhcp_gw = dhcp_gw_dict['gateway'].split('=')
                            bond_line['gateway'] = dhcp_gw[1]
                            dhcp_dns = bond['DHCP4.OPTION[5]:'].split('=')
                            bond_line['dns'] = dhcp_dns[1]
                            #return render_template('test.html', t1=gip)
                        if bond['ipv4.method:'] == 'manual':
                            bond_line['dhcp'] = '手动'
                            gip = bond['ipv4.addresses:']

                            bond_line['gateway'] = bond['ipv4.gateway:']
                            bond_line['dns'] = bond['ipv4.dns:']
                        #assert IPy.IP(gip, make_net=True)
                        ips = IPy.IP(gip, make_net=True)
                        bond_line['ip'] = gip.split('/')[0]
                        bond_line['netmask'] = ips.strNetmask()

        bond_list.append(bond_line)

        #bond_list.append(state)

    #return render_template('test.html', t1=gip, t2=bond_list)
    return render_template('net_bond.html', bond_list=bond_list, dev_info=dev_show())
