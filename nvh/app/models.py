from flask_restful import Resource, reqparse, fields, marshal
from app import tasks,users,auth

task_fields = {
    'title': fields.String,
    'description': fields.String,
    'done': fields.Boolean,
    'uri': fields.Url('task')
}

tasks_fields = {
    'title': fields.String,
    'description': fields.String,
    'done': fields.Boolean,
}

# class UserAPI(Resource):
#     def get(self, id):
#         pass

#     def put(self, id):
#         pass

#     def delete(self, id):
#         pass


class TaskListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'title',
            type=str,
            required=True,
            help='No task title provided',
            location='json')
        self.reqparse.add_argument(
            'description', type=str, default="", location='json')
        super(TaskListAPI, self).__init__()

    def get(self):
        task = [
            marshal(t, tasks_fields) for t in tasks.find({
                'id': {
                    "$gt": 0
                }
            })
        ]
        if task is None:
            abort(404)
        return {'tasks': task}

    def post(self):
        pass


class TaskAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, location='json')
        self.reqparse.add_argument('description', type=str, location='json')
        self.reqparse.add_argument('done', type=bool, location='json')
        super(TaskAPI, self).__init__()

    def get(self, id):
        task = tasks.find_one({'id': id})
        if task is None:
            abort(404)
        return {'task': marshal(task, task_fields)}


    def put(self, id):
        task = tasks.find_one({'id':id})
        if task is None:
            abort(404)
        args = self.reqparse.parse_args()
        for k, v in args.iteritems():
            if v != None:
                task[k] = v
        return {'task': marshal(task, task_fields)}

    def delete(self, id):
        task = tasks.find_one({'id': id})
        if task is None:
            abort(404)
        tasks.remove(task)
        return {'result':True}
