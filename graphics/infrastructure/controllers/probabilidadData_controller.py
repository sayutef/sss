from flask import jsonify, request
from graphics.application.useCases.getProbabilidadData_useCase import GetProbabilityData
from graphics.infrastructure.dependences import getSQLAlchemy

class ProbabilityChartController:
    def __init__(self):
        self.SQLAlchemy = getSQLAlchemy()
        self.use_case = GetProbabilityData(db=self.SQLAlchemy)

    def getProbabilityData(self, days: int = 30):
        try:
            user_id = request.args.get('user_id', 1, type=int)
            data = self.use_case.run(user_id, days)
            return jsonify({
                "status": True,
                "data": {
                    "type": "probability",
                    "chart_type": "line",
                    "attributes": {
                        "days_analyzed": days,
                        "cumulative_weights": data
                    }
                }
            }), 200
        except Exception as e:
            return jsonify({"status": False, "error": str(e)}), 500