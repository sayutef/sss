from flask import jsonify, request
from graphics.application.useCases.getAnilloData_useCase import GetAnilloData
from graphics.infrastructure.dependences import getSQLAlchemy
# from flask_jwt_extended import jwt_required, get_jwt_identity

class AnilloDataController:
    def __init__(self):
        self.SQLAlchemy = getSQLAlchemy()
        self.use_case = GetAnilloData(db=self.SQLAlchemy)
    
    #@jwt_required()
    def getAnilloData(self, days: int = 30):
        try:
            user_id = request.args.get('user_id', 1, type=int) 
            """ user_id = get_jwt_identity()
            if not user_id:
                return jsonify({
                    "status": False,
                    "error": "No se proporcionó ID de usuario."
                }), 401 """
            
            data = self.use_case.run(int(user_id), days)
            
            return jsonify({
                "status": True,
                "data": {
                    "type": "weight_periods",
                    "chart_type": "doughnut",
                    "attributes": {
                        "days_analyzed": days,
                        "total_periods": len(data),
                        "periods": data
                    }
                }
            }), 200
            
        except Exception as e:
            print(f"Error al obtener datos del gráfico anillo: {e}")
            return jsonify({
                "status": False,
                "error": f"Error al obtener datos del gráfico anillo: {e}"
            }), 500