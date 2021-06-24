# -*- coding:utf-8 -*-

from raid.meth import get_cmd_value

'''
dev_show()返回以下列表
[
{'GENERAL.DEVICE:': 'ens192', 'GENERAL.TYPE:': 'ethernet',....}
, {'GENERAL.DEVICE:': 'ens224', 'GENERAL.TYPE:': 'ethernet',....}
{....}
]
'''
def dev_show():
    dev_show_cmd = 'nmcli dev show'
    dev_info = []
    dev_dt = {}
    get_dev = get_cmd_value(dev_show_cmd)
    for dev in get_dev:
        if dev[0] == 'GENERAL.DEVICE:' and len(dev_dt) > 0:
            dev_info.append(dev_dt)
            dev_dt = {}
        value = ''
        for i, v in enumerate(dev):
            if i>0:
                value = value+v+' '
        dev_dt[dev[0]] = value.strip()
    return dev_info

'''
con_show输出结果
{'connection.id:': 'bond0-ens224', 
'connection.uuid:': '4a76e6cd-1aaf-4e1d-aafa-4e4246798b4a',
....
} 
'''
def con_show(con_name):
    cmd = "nmcli con show '"+con_name+"'"
    con_list = get_cmd_value(cmd)
    con_info = {}
    for val in con_list:
        con_key = ''
        con_value = ''
        for i, con in enumerate(val):
            if i == 0:
                con_key = con.strip()
            else:
                con_value = con_value+' '+con
        con_info[con_key] = con_value.strip()
    return con_info
'''
bond_show()返回所有bond列表字典详情
[
{'connection.id:': 'bond0',.... }
{'connection.id:': 'bond0-ens256',.... }
....
]
'''
def bond_show(type):
    bonds = []
    bond = {}
    notbonds = []
    notbond = {}
    con_uuid_list_cmd = "nmcli -t -f uuid con show"
    con_uuid_list = get_cmd_value(con_uuid_list_cmd)
    for con_uuid in con_uuid_list:
        con_info = con_show(con_uuid[0])
        if con_info['connection.type:'] == 'bond' or con_info['connection.slave-type:'] == 'bond':
            bond = con_info
            bonds.append(bond)
        else:
            notbond = con_info
            notbonds.append(notbond)

    if type == 'yes':
        return bonds
    if type == 'no':
        return notbonds