import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from collections import defaultdict
from flask_restful import Api
from task.resources import HelloGeek

USERS_INFO = defaultdict(list)

secret_key = os.environ.get('secret_key')

app = Flask(__name__)
app.config['SECRET_KEY'] = '39348e96bf0b2df9e425fad8c9557228'
app.config['UPLOAD_FOLDER'] = 'E:\\uploads'
# database settings
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)


# settings of login
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = "info"

# Mail Server Settings
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('gmail')
app.config['MAIL_PASSWORD'] = os.environ.get('gmail_password')  # this is google applications password
mail = Mail(app)

# api settings
api = Api(app)
api.add_resource(HelloGeek, '/api')

from task import routes
