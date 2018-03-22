from flask import Flask
from config import Config
from flask_restful import Api
from flask_pymongo import PyMongo
from flask_httpauth import HTTPBasicAuth


def init():
    app = Flask(__name__)
    app.config.from_object(Config)
    return app

app = init()
auth = HTTPBasicAuth()
api = Api(app)
mongo = PyMongo(app)


with app.app_context():
    users=mongo.db.users
    tasks = mongo.db.tasks


# mt = [{
#     'id': 1,
#     'title': u'Buy groceries',
#     'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
#     'done': False
# }, {
#     'id': 2,
#     'title': u'Learn Python',
#     'description': u'Need to find a good Python tutorial on the web',
#     'done': False
# }]

from app import views,models
