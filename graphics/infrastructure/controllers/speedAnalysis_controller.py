from flask import jsonify
from graphics.application.useCases.getSpeedAnalysis_useCase import GetSpeedAnalysis
from graphics.infrastructure.dependences import getSQLAlchemy
# from flask_jwt_extended import jwt_required, get_jwt_identity

class SpeedAnalysisController:
    def __init__(self):
        self.SQLAlchemy = getSQLAlchemy()
        self.use_case = GetSpeedAnalysis(db=self.SQLAlchemy)
    
    #@jwt_required()
    def getSpeedAnalysis(self, days: int, user_id: int):
        try:
            # user_id = get_jwt_identity()
            
            data = self.use_case.run(user_id, days)
            
            return jsonify({
                "status": True,
                "data": {
                    "type": "speed_analysis",
                    "chart_type": "line",
                    "attributes": {
                        "days_analyzed": days,
                        "total_days": len(data),
                        "speed_data": data
                    }
                }
            }), 200
            
        except Exception as e:
            print(f"Error al obtener análisis de velocidad: {e}")
            return jsonify({
                "status": False,
                "error": f"Error al obtener análisis de velocidad: {e}"
            }), 500
