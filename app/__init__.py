from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mysqldb import MySQL

# from config import Config
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate

app = Flask(__name__)
#koneksi
app.secret_key = 'sistemhm'
app.config['MYSQL_HOST'] ='localhost'
app.config['MYSQL_USER'] ='root'
app.config['MYSQL_PASSWORD'] =''
app.config['MYSQL_DB'] ='sistemlayananhm_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
UPLOAD_FOLDER = r'C:\Users\Michael (ASUS)\Documents\Tubes_APSI\folder\uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mysql = MySQL(app)

# db = SQLAlchemy(app)
# migrate = Migrate(app, db)

from app import routes