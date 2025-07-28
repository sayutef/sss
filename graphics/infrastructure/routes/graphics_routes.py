from flask import Blueprint, request
from graphics.infrastructure.controllers.pastelData_controller import PastelDataController
from graphics.infrastructure.controllers.anilloData_controller import AnilloDataController
from graphics.infrastructure.controllers.ojivaData_controller import OjivaDataController
from graphics.infrastructure.controllers.speedAnalysis_controller import SpeedAnalysisController
from graphics.infrastructure.controllers.barraData_controller import BarChartController
from graphics.infrastructure.controllers.correlacionData_controller import CorrelationChartController
from graphics.infrastructure.controllers.probabilidadData_controller import ProbabilityChartController

graphicsBlueprint = Blueprint('graphics', __name__)

@graphicsBlueprint.route('/pastel/<int:user_id>', methods=['GET'])
def getPastelData(user_id):
    days = request.args.get('days', 30, type=int)
    controller = PastelDataController()
    return controller.getPastelData(days, user_id)

@graphicsBlueprint.route('/anillo/<int:user_id>', methods=['GET'])
def getAnilloData(user_id):
    days = request.args.get('days', 30, type=int)
    controller = AnilloDataController()
    return controller.getAnilloData(days, user_id)

@graphicsBlueprint.route('/ojiva/<int:user_id>', methods=['GET'])
def getOjivaData(user_id):
    days = request.args.get('days', 30, type=int)
    controller = OjivaDataController()
    return controller.getOjivaData(days, user_id)

@graphicsBlueprint.route('/speed/<int:user_id>', methods=['GET'])
def getSpeedAnalysis(user_id):
    days = request.args.get('days', 7, type=int)
    controller = SpeedAnalysisController()
    return controller.getSpeedAnalysis(days, user_id)

@graphicsBlueprint.route('/barras/<int:user_id>', methods=['GET'])
def getBarChartData(user_id):
    days = request.args.get('days', 30, type=int)
    controller = BarChartController()
    return controller.getBarChartData(days, user_id)

@graphicsBlueprint.route('/correlacion/<int:user_id>', methods=['GET'])
def getCorrelationData(user_id):
    days = request.args.get('days', 30, type=int)
    controller = CorrelationChartController()
    return controller.getCorrelationData(days, user_id)

@graphicsBlueprint.route('/probabilidad/<int:user_id>', methods=['GET'])
def getProbabilityData(user_id):
    days = request.args.get('days', 30, type=int)
    controller = ProbabilityChartController()
    return controller.getProbabilityData(days, user_id)
