import os
import connexion
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_pymongo import PyMongo
from briket_DB.passwords import connection_mongodb_url

basedir = os.path.abspath(os.path.dirname(__file__))
connex_app = connexion.App(__name__, specification_dir=basedir)

app = connex_app.app

sqlite_url = "sqlite:///" + os.path.join(basedir, "sql_main_files/briket.db")
app.config["SQLALCHEMY_ECHO"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = sqlite_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MONGO_URI"] = connection_mongodb_url
# Create the SqlAlchemy db instance
db = SQLAlchemy(app)

# Initialize Marshmallow
ma = Marshmallow(app)

# Mongo
mongo = PyMongo(app)
mongodb = mongo.db
