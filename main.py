import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

from graphics.infrastructure.dependences import goDependencesGraphics
from graphics.infrastructure.routes.graphics_routes import graphicsBlueprint

from database.db import db
from database.conn.connection import engine

load_dotenv()

# Inicializar Flask y SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = engine.url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")  

CORS(app)
db.init_app(app)

# Inicializar dependencias

goDependencesGraphics()

jwt = JWTManager(app)

# Registrar Blueprints

app.register_blueprint(graphicsBlueprint, url_prefix='/graphics')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1201, debug=True)