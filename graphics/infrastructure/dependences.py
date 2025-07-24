from graphics.infrastructure.adapters.SQLAlchemy import graphicsSQLAlchemy

# Variables globales para las dependencias
alchemy = None

def goDependencesGraphics():
    global alchemy
    alchemy = graphicsSQLAlchemy()

def getSQLAlchemy():
    return alchemy

