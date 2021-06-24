from flask import Blueprint, redirect
from flask_login import login_required
from raid import views

bp = Blueprint('raid', __name__, url_prefix='/raid')

@bp.route('/')
@login_required
def index():
    return views.index()

@bp.route('/info/<raid_name>')
@login_required
def raid_info(raid_name):
    return views.raid_info(raid_name)

@bp.route('/raid_create/', methods=['POST', 'GET'])
@login_required
def raid_create():
    return views.raid_create()

@bp.route('/raid_change_dev/', methods=['POST', 'GET'])
@login_required
def raid_change_dev():
    return views.raid_change_dev()

@bp.route('/raid_del/')
@login_required
def raid_del():
    #views.raid_del()
    return views.raid_del()

@bp.route('/test/')
@login_required
def test():
    return views.test()