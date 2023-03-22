from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
import os

load_dotenv()
db = SQLAlchemy()
auth = HTTPBasicAuth()
users = {
    "narumi": generate_password_hash(os.getenv('N_PASS')),
    "takeru": generate_password_hash(os.getenv('T_PASS')),
}



def create_app():
    app = Flask(__name__)

    app.config['JSON_AS_ASCII'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # ルートをインポートします
    from .routes import main
    app.register_blueprint(main)

    return app
