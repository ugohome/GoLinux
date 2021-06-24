# -*- coding: utf-8 -*-

from flask import Blueprint
from flask_login import login_required
from DRS import views

drs_bp = Blueprint('drs', __name__, url_prefix='/drs/')


@drs_bp.route('/', methods=['POST', 'GET'])
@login_required
def index():
    return views.index()

@drs_bp.route('/update/', methods=['POST', 'GET'])
@login_required
def update():
    return views.update()