# -*- coding:utf-8 -*-

from flask import request, render_template, redirect
from raid.meth import get_cmd_value
from NAS import share

def index():
    submit = request.form.get('submit')
    type = request.args.get('type')
    if submit:
        nas_share_set()
        return redirect('/raid/')
    md_name = request.args.get('md_name')
    md_mount_path = request.args.get('md_mount_path')
    share_conf = share.get_smb_conf('share')

    return render_template('nas.html', md_name=md_name, md_mount_path=md_mount_path, share_conf=share_conf, type=type)

def nas_global_set():
    global_info = share.get_smb_conf('global')
    share_info = share.get_smb_conf('share')
    unit = {}
    unit['unit_name'] = request.form.get('type')
    link_max = request.form.get('link_max')
    if link_max:
        unit['max connections'] = link_max
    allow = request.form.get('allow')
    if allow:
        unit['hosts allow'] = allow
    deny = request.form.get('deny')
    if deny:
        unit['hosts deny'] = deny
    submit = request.form.get('submit')

    if submit:
        share.write_smb_conf(unit, share_info)
        return redirect('/raid/')
        #return render_template('test.html', t1=unit)
    return render_template('nas_global_set.html', global_info=global_info)

def nas_share_set():
    get_unit = {}
    submit = request.form.get('submit')
    unit_name_old = request.form.get('unit_name_old')
    unit_name = request.form.get('unit_name')
    if unit_name:
        if unit_name[0]+unit_name[-1] != '[]':
            unit_name = '['+unit_name+']'
        get_unit['unit_name'] = unit_name
    comment = request.form.get('comment')
    if comment:
        get_unit['comment'] = comment
    path = request.form.get('path')
    if path:
        get_unit['path'] = path
        get_cmd_value('mkdir -p '+path)
    browseable = request.form.get('browseable')
    if browseable:
        get_unit['browseable'] = browseable
    writeable = request.form.get('writeable')
    if writeable:
        get_unit['writeable'] = writeable
    valid_users = request.form.get('valid_users')
    if valid_users:
        get_unit['valid users'] = valid_users
    directory_mask = request.form.get('directory_mask')
    if directory_mask:
        get_unit['directory mask'] = directory_mask
    invalid_users = request.form.get('invalid_users')
    if invalid_users:
        get_unit['invalid users'] = invalid_users
    write_list = request.form.get('write_list')
    if write_list:
        get_unit['write list'] = write_list

    global_unit = share.get_smb_conf('global')
    share_unit = share.get_smb_conf('share')
    #share_unit['old']=unit_name_old
    #return  share_unit

    if submit != '新增':
        del share_unit[unit_name_old]
    if submit == '修改' or submit == '新增':
        get_cmd_value('mkdir -p '+path)
        get_cmd_value('chmod -R 777 '+path)
        share_unit[unit_name] = get_unit
    share.write_smb_conf(global_unit, share_unit)

def nas_user():
    passwd_cmd = "echo -e 'abc\nabc'|smbpasswd -s test"
    show_user = get_cmd_value("pdbedit -L|awk -F : '{print($1)}'")
    user_name = request.args.get('user_name')
    pwd = request.args.get('pwd')
    type = request.args.get('type')
    submit = request.form.get('submit')
    users = request.form.getlist('users')
    if submit == '删除':
        #return render_template('test.html', t1=users)

        for u in users:
            del_smb_user = 'smbpasswd -x ' + u
            del_user = 'userdel -r ' + u
            get_cmd_value(del_smb_user)
            get_cmd_value(del_user)
        return redirect('/nas/nas_user/')


    if type == 'mody_pwd':
        mody_pwd_cmd = "echo -e '"+pwd+"\n"+pwd+"'|smbpasswd -s "+user_name
        get_cmd_value(mody_pwd_cmd)

    if type == 'create_user':
        create_user_cmd = 'useradd -s /sbin/nologin '+pwd
        get_cmd_value(create_user_cmd)
        create_smb_user_cmd = "echo -e 'abc@123\nabc@123'|smbpasswd -as " + pwd
        get_cmd_value(create_smb_user_cmd)
        return redirect('/nas/nas_user/')

    return render_template('nas_user.html', show_user=show_user)
