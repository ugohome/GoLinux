# -*- coding: utf-8 -*-
from flask import Blueprint
from flask_login import login_required
from system import views

bp = Blueprint('system', __name__, url_prefix='/system')
#必需使用url_prefix,否则蓝图的路由变面http://host:port/,而不会是http://host:port/system

@bp.route('/', methods=['POST', 'GET'])
@login_required
def index():
    return views.index()

@bp.route('/process/')
@login_required
def process():
    return views.process()