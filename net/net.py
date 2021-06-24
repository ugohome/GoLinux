# -*- coding:utf-8 -*-

from flask import Blueprint
from flask_login import login_required
from net import views

net_bp = Blueprint('net', __name__, url_prefix='/net/')

@net_bp.route('/', methods=['POST', 'GET'])
@login_required
def index():
    return views.index()

@net_bp.route('/net_mod/', methods=['POST', 'GET'])
@login_required
def net_mod():
    return views.net_mod()

@net_bp.route('/net_bond/', methods=['POST', 'GET'])
@login_required
def net_bond():
    return views.net_bond()

