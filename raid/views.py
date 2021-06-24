from os import remove
from flask import render_template, request, redirect, url_for
from raid.meth import get_cmd_value, MdInfo
from NAS import share, views
from system.share import get_hum_data
from unittest import TestCase
from flask import json

def test():
    ts = TestCase()
    t1 = request.args.get('t1')
    if 't1' not in dir():
        t1 = 1
    #ts.assertEqual(t1, 'hello')
    #jst = ['h', 1, 2, {'a': 100}]
    #return json.dumps(jst)
    return render_template('test.html', test=get_hum_data(float(t1)))

def index():
    md_name = request.args.get('md_name')
    mount_path = request.args.get('mount_path')
    type = request.args.get('type')
    mdname_cmd = "cat /proc/mdstat |grep ^md|awk '{print($1)}'"
    mdname = get_cmd_value(mdname_cmd)
    mds = []

    for l in mdname:
        mdinfo = MdInfo(l[0])
        stat = mdinfo.md_value('State.:')
        md_level = get_cmd_value('mdadm -D /dev/' + l[0] + '|grep Raid.Level')
        md_mount = get_cmd_value('df -h |grep -w '+l[0])
        if md_mount[0][0] == 'ERROR':
            md_line = [l[0], md_level[0][3], stat, '']
            #return render_template('test.html', t1=md_mount, t2=md_line[3])
        else:
            md_line = [l[0], md_level[0][3], stat, md_mount[0][5]]
            #return render_template('test.html', t1=md_mount)
        mds.append(md_line)

    if type == 'mount' and mount_path != '':
        mk_path_cmd = 'mkdir -p '+mount_path
        get_cmd_value(mk_path_cmd)
        mount_cmd = 'mount /dev/'+md_name+' '+mount_path
        get_cmd_value(mount_cmd)
        get_cmd_value("tail -n 1 /etc/mtab >> /etc/fstab")
        return redirect('/raid/')

    if type == 'umount' and mount_path != '':
        umount_cmd = 'umount '+mount_path
        get_cmd_value(umount_cmd)
        lines = (i for i in open('/etc/fstab', 'r') if mount_path not in i)
        remove('/etc/fstab')
        with open('/etc/fstab', 'w') as fw:
            fw.writelines(lines)
        return redirect('/raid/')

    return render_template('raid.html', mdtitle=mds)

def raid_info(raid_name):
    dev = '/dev/' + raid_name

    #获取RAID大小
    md_size_cmd = 'df -h|grep -w ' + dev
    md_size_info = get_cmd_value(md_size_cmd)
    if md_size_info[0][0] == 'ERROR':
        md_size_cmd = 'mdadm -q ' + dev
        md_size_info = get_cmd_value(md_size_cmd)

    #获取RAID基础信息
    mdinfo = MdInfo(raid_name)
    stat = mdinfo.md_value('State.:')
    level = mdinfo.md_value('Raid.Level')
    rebuild = mdinfo.md_value('Status')
    chunk = mdinfo.md_value('Chunk.Size')
    us_size = ''
    used_size = mdinfo.md_value('Used.Dev.Size')
    if len(used_size) != 0:
        begin = used_size.index('(')+1
        end = used_size.index('B')+1
        us_size = used_size[begin:end]
    md_info = [raid_name, level, stat, chunk, rebuild, us_size]

    # 获取RAID磁盘信息
    md_devs = mdinfo.md_dev()

    #return render_template('test.html', test=md_devs)
    return render_template('raid_info.html', md_info=md_info, md_size_info=md_size_info, md_devs=md_devs)

def raid_create():
    #disks = get_cmd_value('lsblk -dn')
    mdinfo = MdInfo('md0')
    disks = mdinfo.md_not_dev()
    disk_info = mdinfo.md_not_dev_info()
    #disk_info = get_cmd_value('lsblk -n')
    md_disks = request.form.getlist('md_disks')
    md_level = request.form.get('level')
    md_chunk = request.form.get('chunk')
    md_spare = request.form.get('md_spare')

    #在已有的RAID名下获取新RAID名.
    get_md_number = get_cmd_value("cat /proc/mdstat |grep ^md|awk '{print($1)}'")
    if len(get_md_number) == 0:
        new_md_name = 'md0'
    else:
        md_number = []
        for name in get_md_number:
            md_number.append(int(name[0][2:]))
        new_md_number = max(md_number)+1
        new_md_name = 'md'+str(new_md_number)

    md_create_cmd = ''
    run_create = ''
    if md_level is not None and len(md_disks) >= 2:
        #echo -e 'y' |mdadm -C /dev/md128 -l 0 -n 2 /dev/sdc /dev/sdd
        #使用以上命令,防止创建RAID时由于已有分区表信息需要手动输入y确认创建RAID.
        md_create_cmd = 'mdadm -C /dev/' + new_md_name + ' -c '+ md_chunk + ' -l ' + md_level
        if md_spare is not None:
            md_create_cmd = md_create_cmd + ' -x ' + md_spare
            dev_number = len(md_disks)-int(md_spare)  #计算RAID盘数=设备总数-执备盘
            md_create_cmd = md_create_cmd + ' -n ' + str(dev_number)
        else:
            md_create_cmd = md_create_cmd + ' -n ' + str(len(md_disks))
        for d in md_disks:
            md_create_cmd = md_create_cmd + ' /dev/' + d + ' '
            #get_cmd_value('./sh/fd.sh /dev/' + d)

        run_create = get_cmd_value("./sh/md.sh '"+md_create_cmd+"'")
        get_cmd_value('mkfs.ext4 /dev/'+new_md_name)
        #return render_template('test.html', t1=run_create)
        return redirect('/raid/')

    return render_template('raid_create.html', disks=disks, disk_info=disk_info, md_disks=run_create)

def raid_change_dev():
    md_name = request.args.get('md_name')
    md_dev = request.args.get('md_dev')
    type = request.args.get('type')
    #disks = get_cmd_value('lsblk -dn')
    mdinfo = MdInfo('md0')
    disks = mdinfo.md_not_dev()
    disks_info = mdinfo.md_not_dev_info()
    #disks_info = get_cmd_value('lsblk -n')

    newdisk = request.form.get('newdisk')
    md_name_fm = request.form.get('md_name')
    md_dev_fm = request.form.get('md_dev')
    type_fm = request.form.get('type')
    if type == 'rm_faulty_dev':
        #md_fail_dev_cmd = 'mdadm --manage /dev/' + md_name + ' --fail ' + md_dev
        #get_cmd_value(md_fail_dev_cmd)
        md_remove_dev_cmd = 'mdadm --manage /dev/' + md_name + ' --remove ' + md_dev
        get_cmd_value(md_remove_dev_cmd)
        del_super_cmd = 'mdadm --zero-superblock ' + md_dev
        get_cmd_value(del_super_cmd)
        return redirect('/raid/info/' + md_name)
    elif type == 'ext_new_dev':
        mdinfo = MdInfo(md_name)
        active_dev = mdinfo.md_value('Active.Devices')
        active_dev_n = int(active_dev) + 1
        md_ext_cmd = 'mdadm --grow /dev/' + md_name + ' -n ' + str(active_dev_n)
        get_cmd_value(md_ext_cmd)
        #return render_template('test.html', test=md_ext_cmd)
        return redirect('/raid/info/'+md_name)
    elif type=='refresh_md':
        mdinfo = MdInfo(md_name)
        md_not_dev = mdinfo.md_not_dev()
        for d in md_not_dev:
            get_cmd_value('mdadm --manage /dev/'+md_name+' --re-add /dev/'+d)
        md_ext_fs_cmd = 'resize2fs /dev/' + md_name
        get_cmd_value(md_ext_fs_cmd)
        return redirect('/raid/info/'+md_name)
        #return render_template('test.html', t1=cmd)

    if newdisk is not None:
        md_add_dev_cmd = 'mdadm --manage /dev/'+md_name_fm+' --add /dev/'+newdisk
        get_cmd_value(md_add_dev_cmd)
        if type_fm == 'ext_new_dev':
            mdinfo = MdInfo(md_name_fm)
            active_dev = mdinfo.md_value('Active.Devices')
            active_dev_n = int(active_dev)+1
            md_ext_cmd = 'mdadm --grow /dev/' + md_name_fm + ' -n ' + str(active_dev_n)
            md_ext = get_cmd_value(md_ext_cmd)
            #type_fm = md_ext_cmd
        #return render_template('test.html', test=type_fm)
        return redirect('/raid/info/'+md_name_fm)

    return render_template('raid_change_dev.html', md_name=md_name, md_dev=md_dev,
                           newdisk=newdisk, disks=disks, disks_info=disks_info)

def raid_del():
    md_name = request.args.get('md_name')
    md_dev = '/dev/'+md_name
    md_mount = get_cmd_value('df -h |grep -w '+md_dev)

    #卸载RAID
    if md_mount[0][0] != 'ERROR':
        get_cmd_value('umount '+md_mount[0][5])
        #根据RAID名称,删除启动自动挂载,如果是UUID挂载无法删除.
        get_cmd_value("sed -i '/" + md_name + "/d' /etc/fstab")

    #清除RAID超级块信息
    mdinfo = MdInfo(md_name)
    md_devs = mdinfo.md_dev()
    get_cmd_value('mdadm -S ' + md_dev)    #停止RAID必需放在获取RAID DEV后面,不然mdinfo.md_dev()就为空了.
    #delcmd = []
    for dev in md_devs:
        del_super_cmd = 'mdadm --zero-superblock '+dev[1]
        delsup = get_cmd_value(del_super_cmd)
        #delcmd.append(delsup)
    #get_cmd_value('mdadm --remove '+md_dev)
    #get_cmd_value('mdadm -Ds > /etc/mdadm.conf')

    return redirect('/raid/')
    #return render_template('test.html', test=del_super_cmd, t1=md_devs, t2=delcmd)

def raid_ext():
    md_name = request.args.get('md_name')
    md_dev = request.args.get('md_dev')
    md_work_dev = request.args.get('md_work_dev')+1
    md_add_dev = 'mdadm /dev/md0 --add /dev/sde'
    md_ext_dev = 'mdadm --grow /dev/md0 -n 4'