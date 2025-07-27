from flask import Blueprint, request
from graphics.infrastructure.controllers.pastelData_controller import PastelDataController
from graphics.infrastructure.controllers.anilloData_controller import AnilloDataController
from graphics.infrastructure.controllers.ojivaData_controller import OjivaDataController
from graphics.infrastructure.controllers.speedAnalysis_controller import SpeedAnalysisController
from graphics.infrastructure.controllers.barraData_controller import BarChartController
from graphics.infrastructure.controllers.correlacionData_controller import CorrelationChartController
from graphics.infrastructure.controllers.probabilidadData_controller import ProbabilityChartController

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

@graphicsBlueprint.route('/barras', methods=['GET'])
def getBarChartData():
    days = request.args.get('days', 30, type=int)
    controller = BarChartController()
    return controller.getBarChartData(days)

@graphicsBlueprint.route('/correlacion', methods=['GET'])
def getCorrelationData():
    days = request.args.get('days', 30, type=int)
    controller = CorrelationChartController()
    return controller.getCorrelationData(days)

@graphicsBlueprint.route('/probabilidad', methods=['GET'])
def getProbabilityData():
    days = request.args.get('days', 30, type=int)
    controller = ProbabilityChartController()
    return controller.getProbabilityData(days)