from flask import Blueprint, request
from graphics.infrastructure.controllers.pastelData_controller import PastelDataController
from graphics.infrastructure.controllers.anilloData_controller import AnilloDataController
from graphics.infrastructure.controllers.ojivaData_controller import OjivaDataController
from graphics.infrastructure.controllers.speedAnalysis_controller import SpeedAnalysisController

graphicsBlueprint = Blueprint('graphics', __name__)

@graphicsBlueprint.route('/pastel', methods=['GET'])
def getPastelData():
    days = request.args.get('days', 30, type=int)
    controller = PastelDataController()
    return controller.getPastelData(days)

@graphicsBlueprint.route('/anillo', methods=['GET'])
def getAnilloData():
    days = request.args.get('days', 30, type=int)
    controller = AnilloDataController()
    return controller.getAnilloData(days)

@graphicsBlueprint.route('/ojiva', methods=['GET'])
def getOjivaData():
    days = request.args.get('days', 30, type=int)
    controller = OjivaDataController()
    return controller.getOjivaData(days)

@graphicsBlueprint.route('/speed', methods=['GET'])
def getSpeedAnalysis():
    days = request.args.get('days', 7, type=int)
    controller = SpeedAnalysisController()
    return controller.getSpeedAnalysis(days)