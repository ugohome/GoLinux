# -*- coding:utf-8 -*-

from flask import Blueprint
from flask_login import login_required
from NAS import views

nas_bp = Blueprint('nas', __name__, url_prefix='/nas')

@nas_bp.route('/', methods=['POST', 'GET'])
@login_required
def index():
    return views.index()

@nas_bp.route('/nas_global_set/', methods=['POST', 'GET'])
@login_required
def nas_global_set():
    return views.nas_global_set()

@nas_bp.route('/nas_user/', methods=['POST', 'GET'])
@login_required
def nas_user():
    return views.nas_user()