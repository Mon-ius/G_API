import os
basedir = os.path.abspath(os.path.dirname(__file__))
class Config(object):
    POSTS_PER_PAGE = 3
    MONGO_DBNAME='api'
    MONGO_URI='mongodb://api:HUtGhognajghif6@ds213759.mlab.com:13759/api'
    SECRET_KEY = os.environ.get('SECRET_KEY') or \
                    'you-will-never-guess'