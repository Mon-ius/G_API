from flask import Flask, jsonify, abort, make_response, url_for, redirect, render_template, session,request,g


from app import app,api,mongo,users,tasks,auth
from .models import  TaskListAPI, TaskAPI
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature


# api.add_resource(UserAPI, '/users/<int:id>', endpoint = 'user')
api.add_resource(TaskListAPI, '/todo/api/v1.0/tasks', endpoint = 'tasks')
api.add_resource(TaskAPI, '/todo/api/v1.0/tasks/<int:id>', endpoint = 'task')



@auth.verify_password
def verify_password(username_or_token, password):
    s = Serializer(app.config['SECRET_KEY'])
    data =None
    user = None
    try:
        data = s.loads(username_or_token)
    except SignatureExpired:
        data = None  # valid token, but expired
    except BadSignature:
        data = None  # invalid token
    if data:
        user = users.find_one({'id': data['id']})
    if not user:
        user = users.find_one({'username': username_or_token})
        if not user or not pwd_context.verify(password, user['password']):
            return False
    g.user = user
    return True


@app.route('/api/token')
@auth.login_required
def get_auth_token():
    expiration=600
    s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
    token = s.dumps({'id': g.user['id']})
    return jsonify({'token': token.decode('ascii')})




@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/')
@auth.login_required
def index():
    return "Hello, {}!".format(auth.username())


@app.route('/api/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)  # missing arguments
    if users.find_one({'username': username}) is not None:
        abort(400)  # existing user
    password_hash = pwd_context.encrypt(password)
    userid = int(users.count()) + 1
    user = {'id': userid, 'username': username, 'password': password_hash}
    users.insert(user)
    return jsonify({
        'username': username
    }), 201, {
        'Location': url_for('get_user', userid=userid, _external=True)
    }
    # return jsonify({
    #     'Location':
    #     url_for('get_user', userid=userid, _external=True)
    # })


@app.route('/api/users/<int:userid>')
def get_user(userid):
    user = users.find_one({'id': userid})
    if not user:
        abort(400)
    return jsonify({'username': user['username']})


@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user['username']})


# @app.route('/todo/api/v1.0/tasks', methods=['POST'])
# def create_task():
#     if not request.json or not 'title' in request.json:
#         abort(400)
#     task = {
#         'id': tasks[-1]['id'] + 1,
#         'title': request.json['title'],
#         'description': request.json.get('description', ""),
#         'done': False
#     }
#     tasks.append(task)
#     return jsonify({'task': task}), 201
