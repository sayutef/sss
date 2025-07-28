from flask import jsonify
from graphics.application.useCases.getOjivaData_useCase import GetOjivaData
from graphics.infrastructure.dependences import getSQLAlchemy
# from flask_jwt_extended import jwt_required, get_jwt_identity

class OjivaDataController:
    def __init__(self):
        self.SQLAlchemy = getSQLAlchemy()
        self.use_case = GetOjivaData(db=self.SQLAlchemy)
    
    # @jwt_required()
    def getOjivaData(self, days: int, user_id: int):
        try:
            # user_id = get_jwt_identity()
            
            data = self.use_case.run(user_id, days)
            
            return jsonify({
                "status": True,
                "data": {
                    "type": "distance_cumulative",
                    "chart_type": "ogive",
                    "attributes": {
                        "days_analyzed": days,
                        "total_readings": len(data),
                        "cumulative_data": data
                    }
                }
            }), 200
            
        except Exception as e:
            print(f"Error al obtener datos del gráfico ojiva: {e}")
            return jsonify({
                "status": False,
                "error": f"Error al obtener datos del gráfico ojiva: {e}"
            }), 500
