import sys
print("Test import progressivo...")
print()

print("[1] Import flask...")
sys.stdout.flush()
import flask
print("    OK - Flask version:", flask.__version__)
sys.stdout.flush()

print("[2] Import sqlalchemy...")
sys.stdout.flush()
import sqlalchemy
print("    OK - SQLAlchemy version:", sqlalchemy.__version__)
sys.stdout.flush()

print("[3] Import flask_sqlalchemy...")
sys.stdout.flush()
import flask_sqlalchemy
print("    OK - Flask-SQLAlchemy version:", flask_sqlalchemy.__version__)
sys.stdout.flush()

print("[4] Creare istanza SQLAlchemy...")
sys.stdout.flush()
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
print("    OK - Istanza creata")
sys.stdout.flush()

print()
print("TUTTO OK! Il problema e' altrove.")



















