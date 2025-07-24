from flask import jsonify, request
from graphics.application.useCases.getPastelData_useCase import GetPastelData
from graphics.infrastructure.dependences import getSQLAlchemy
# from flask_jwt_extended import jwt_required, get_jwt_identity

class PastelDataController:
    def __init__(self):
        self.SQLAlchemy = getSQLAlchemy()
        self.use_case = GetPastelData(db=self.SQLAlchemy)
    
    #@jwt_required()
    def getPastelData(self, days: int = 30):
        try:
            # user_id = get_jwt_identity()
            user_id = request.args.get('user_id', 1, type=int) 
            #if not user_id:
             #   return jsonify({
              #      "status": False,
               #     "error": "No se proporcionó ID de usuario."
                #}), 401
            
            data = self.use_case.run(int(user_id), days)
            
            return jsonify({
                "status": True,
                "data": {
                    "type": "waste_distribution",
                    "chart_type": "pie",
                    "attributes": {
                        "days_analyzed": days,
                        "total_types": len(data),
                        "distribution": data
                    }
                }
            }), 200
            
        except Exception as e:
            print(f"Error al obtener datos del gráfico pastel: {e}")
            return jsonify({
                "status": False,
                "error": f"Error al obtener datos del gráfico pastel: {e}"
            }), 500