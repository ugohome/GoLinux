from subprocess import run, PIPE

#返回命令执行后的序列,cmdvalues[行序号][列序号],如'ls -l'命令输出结果第2行第3列字典表示为cmdvalues[1][2]
def get_cmd_value(cmd):
    cmdlinevalue = []  # 保存命令输出后每行的所有字段
    cmdvalues = []  #按行保存所有字段.
    #n = 0
    m = 0
    cmd = run(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    outstr = cmd.stdout.decode()
    outlines = outstr.split('\n')

    if cmd.returncode == 0:
        for line in outlines:
            n = 0
            cmdlinevalue = []  #每次取行后必需置空.
            if line != '':
                values = line.split()
                for v in values:
                    cmdlinevalue.append(v)
                    n += 1
                cmdvalues.append(cmdlinevalue)
                m += 1
    else:
        cmdlinevalue = ['ERROR', cmd.stderr.decode()]
        cmdvalues = [cmdlinevalue]  #使用2层列表格式生成列表套列表,cmdvalues.append(cmdlinevalue)只能生成单层列表.
    return cmdvalues

class MdInfo:

    def __init__(self, md_name):
        self.md_name = md_name

    #截取RAID详细信息中的属性值,如:Raid Level : raid5截取后为raid5
    def md_value(self, value):
        cmd = "mdadm -D /dev/" + self.md_name + "|grep "+value+"|awk -F : '{print($2)}'"
        get_value = get_cmd_value(cmd)
        if len(get_value) == 0:
            md_value = ''
        else:
            md_value = ''.join(get_value[0])
        return md_value

    # 获取RAID磁盘信息
    def md_dev(self):
        md_devs = []
        y = 0
        md_dev_line = get_cmd_value('cat /proc/mdstat |grep -w ' + self.md_name)
        for i, v in enumerate(md_dev_line[0]):  # enumerate可以获取当前FOR的索引值
            if y == 1:
            #if i > 3:
                if '[' in v:
                    n = v.index('[')  # 获取字符串中特定字符的索引位置sdb1[3]为4
                    md_dev_name = v[:n]  # 根据索引位置截取需要的字符,sdb1
                    md_dev_cmd = "mdadm -D /dev/" + self.md_name + " |grep -w " + md_dev_name + "|awk '{print($4,$7,$6,$5)}'"
                    md_dev_list = get_cmd_value(md_dev_cmd)
                    if len(md_dev_list) !=0:
                        md_devs.append(md_dev_list[0])
            if 'raid' in v or v == 'inactive':
                y = 1

        md_remove_dev_cmd = "mdadm -D /dev/"+self.md_name+" |grep removed|awk '{print($4,$7,$6,$5)}'"
        md_removed_dev = get_cmd_value(md_remove_dev_cmd)

        if len(md_removed_dev) != 0:
            for line in md_removed_dev:
                line.insert(1, '')
                md_devs.append(line)

        return md_devs

    def md_all_devs(self):
        md_devs = []
        md_devs_cmd = get_cmd_value('cat /proc/mdstat |grep ^md')
        for line in md_devs_cmd:
            y = 0
            for v in line:
                if y == 1:
                    md_devs.append(v[:3])
                if 'raid' in v or v == 'inactive':
                    y = 1
        return md_devs

    def md_not_dev(self):
        not_mddev = []
        all_dev = get_cmd_value("lsblk -dn|awk '{print($1)}'")
        md_dev = self.md_all_devs()
        for line in all_dev:
            for v in line:
                if v not in md_dev:
                    not_mddev.append(v)
        return not_mddev

    def md_not_dev_info(self):
        notmd_dev_info = []
        notmd_dev = self.md_not_dev()
        for d in notmd_dev:
            cmd = "lsblk -n /dev/" + d + "|awk '{print($1,$4,$7)}'"
            devinfo = get_cmd_value(cmd)
            notmd_dev_info.append(devinfo)
        return notmd_dev_info