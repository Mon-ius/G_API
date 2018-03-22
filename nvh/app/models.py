from flask_restful import Resource, reqparse, fields, marshal
from passlib.apps import custom_app_context as pwd_context
from app import tasks,users,auth
from flask import abort,url_for
task_fields = {
    'title': fields.String,
    'description': fields.String,
    'done': fields.Boolean,
    'uri': fields.Url('task')
}

tasks_fields = {
    'id':fields.Integer,
    'title': fields.String,
    'description': fields.String,
    'done': fields.Boolean,
}

def abort_if_task_doesnt_exist(id):
    task = tasks.find_one({'id': id})
    if not task:
        abort(400, "Task {} doesn't exist".format(id))
    return task

class UserAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type=str,required=True,help='username required', location='json')
        self.reqparse.add_argument('password', type=str,required=True,help='password required', location='json')
        super(UserAPI, self).__init__()
    # def get(self, id):
    #     pass

    def post(self):
        args = self.reqparse.parse_args()
        username = args['username']
        password = args['password']
        if users.find_one({'username': username}) is not None:
            abort(400)  # existing user
        password_hash = pwd_context.encrypt(password)
        userid = int(users.count()) + 1
        user = {'id': userid, 'username': username, 'password': password_hash}
        users.insert(user)
        return {
            'username': username
        }, 201, {
            'Location': url_for('get_user', userid=userid, _external=True)
        }
       



class TaskAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, location='json')
        self.reqparse.add_argument('description', type=str, location='json')
        self.reqparse.add_argument('done', type=bool, location='json')
        super(TaskAPI, self).__init__()

    def get(self, id):
        task=abort_if_task_doesnt_exist(id)
        return {'task': marshal(task, task_fields)}


    def put(self, id):
        task=abort_if_task_doesnt_exist(id)
        args = self.reqparse.parse_args()
        for k, v in args.items():
            if v != None:
                task[k] = v
        tasks.save(task)
        return {'task': marshal(task, task_fields)}

    def delete(self, id):
        task=abort_if_task_doesnt_exist(id)
        tasks.remove(task)
        return {'result':True}

class TaskListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title',type=str,required=True,help='No task title provided',location='json')
        self.reqparse.add_argument('description', type=str, default="", location='json')
        super(TaskListAPI, self).__init__()

    def get(self):
        task = [t for t in tasks.find({'id': {"$gt": 0}})]
        if not len(task):
            abort(400,"Tasks doesn't exist")
        task = list(map(lambda x: marshal(x,tasks_fields), task))
        
        return {'tasks': task}

    def post(self):
        
        t = {
        'id': None,
        'title':None ,
        'description':None,
        'done': False
        }
        
        args = self.reqparse.parse_args()
        for k, v in args.items():
            if v != None:
                t[k] = v
        t['id']=tasks.count()+1
        # t['id']=30
        tasks.insert(t)
        return {'task': marshal(t,tasks_fields)}



