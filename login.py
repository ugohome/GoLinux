# -*- coding:utf-8 -*-

from flask_login import UserMixin, login_user
from flask import request, redirect, render_template, url_for
from werkzeug.security import check_password_hash, generate_password_hash
'''
users = [
    {'id':'admin', 'username':'administrator', 'password':'abc@123'}
]
'''
with open('static/pwd') as pwd_file:
    pwds = pwd_file.readlines()
    users = []
    for p in pwds:
        line = p.split(':')
        userline = {}
        userline['id'] = line[0]
        userline['username'] = line[1]
        userline['password'] = line[2].split()[0]
        users.append(userline)


class User(UserMixin):

    def __init__(self, username):
        self.username = username
        self.id = self.get_id()     #User.id必需附值,用于存储session(id),也可以在实例化后附值User.id = 'user_id'

    def get_id(self):
        for user in users:
            if self.username == user['username']:
                return user['id']

    #定义一个静态方法,可以直接使用User.get_User(user_id)调用,不需要实例化与类方法无关.
    #该方法反回一个User实例,用于回调函数中返回User对像.
    @staticmethod
    def get_User(user_id):
        for user in users:
            if user_id == user['id']:
                return User(user['username'])

def login():
    if request.method == 'POST':
        user_name = request.form.get('username')
        password = request.form.get('password')
        for user in users:
            if user_name == user['username'] and password == user['password']:
                curr_user = User(user_name)
                #保存登陆状态(保存session信息),User对像必需有id值,如果User未附值,
                # 可在实例对像中附值(curr_user.id=user['id']),回调函数通过这个id重载一个User对像判断用户登陆状态.
                login_user(curr_user, remember=True)
                #return redirect('/')
    return render_template('index.html')