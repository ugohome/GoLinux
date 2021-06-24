# -*- coding:utf-8 -*-

import os
from flask import render_template
from raid.meth import get_cmd_value

def get_smb_conf(type):
    smb_conf_info = {}
    n = 0

    with open('/etc/samba/smb.conf', 'r') as smb_conf:
        for line in smb_conf.readlines():
            line_split = line.split('=')
            if len(line_split)==1 and '[' in line_split[0]:
                line_split.insert(0, 'unit_name')
                #line_split.append('')

            if 'unit_name' in line_split :
                n += 1
                unit = {}
                unit_name = line_split[1].strip()

            if n > 0 and len(line_split) > 1:
                unit[line_split[0].strip()] = line_split[1].strip()
                smb_conf_unit = 'smb_conf_unit'+str(n-1)
                #smb_conf_info[smb_conf_unit] = unit
                smb_conf_info[unit_name] = unit

    smb_share = {}
    for unit in smb_conf_info:
        if '[global]' in smb_conf_info[unit]['unit_name']:
            smb_global = smb_conf_info[unit]
        else:
            smb_share[unit] = smb_conf_info[unit]
    #return smb_conf_info

    if type=='global':
        return smb_global
    else:
        return smb_share

def write_smb_conf(global_unit, share_unit):
    now_path = os.path.abspath(os.path.dirname(__file__))  # 获取当前路径'/pyst/PTL/DRS/'
    base_path = os.path.dirname(now_path)
    smb_con_file = os.path.join(base_path, 'templates/')+'auto_smb.conf'
    global_set_temp = render_template('smb_template.conf', unit=global_unit)
    with open(smb_con_file, 'w') as f:
        f.write(global_set_temp)
        for un in share_unit:
            share_set_temp = render_template('smb_template.conf', unit=share_unit[un])
            f.write(share_set_temp)

    cp_smb_conf = 'cp -rf '+smb_con_file+' /etc/samba/smb.conf'
    #cp_smb_conf = 'cp -rf templates/auto_smb.conf /etc/samba/smb.conf'
    get_cmd_value(cp_smb_conf)
    get_cmd_value('systemctl restart smb')