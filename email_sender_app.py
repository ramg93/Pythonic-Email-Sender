from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
db_name = "esa.db"
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_name}'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from routes import *

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
