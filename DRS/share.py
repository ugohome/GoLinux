from raid.meth import get_cmd_value

def get_svr_info(svr_name):
    svr_auto = get_cmd_value("systemctl status -l "+svr_name+"|grep 'Loaded:'|awk '{print($4)}'")
    svr_state = get_cmd_value("systemctl status -l "+svr_name+"|grep 'Active:'|awk '{print($2,$3)}'")

    svr_info = {}
    svr_info['svr_name'] = svr_name
    svr_info['svr_auto'] = svr_auto[0][0].rstrip(';')
    svr_info['svr_state'] = svr_state[0][0]+svr_state[0][1]

    return svr_info