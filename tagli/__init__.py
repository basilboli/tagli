from flask import Flask
from flask.ext.pymongo import PyMongo

app = Flask(__name__)
app.config["MONGODB_SETTINGS"] = {'DB': "tagli"}
app.config["SECRET_KEY"] = "tagli"

mongo = PyMongo(app)

if __name__ == '__main__':
    app.run()