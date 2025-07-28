from flask import jsonify
from graphics.application.useCases.getCorrelacion_useCase import GetCorrelationData
from graphics.infrastructure.dependences import getSQLAlchemy

class CorrelationChartController:
    def __init__(self):
        self.SQLAlchemy = getSQLAlchemy()
        self.use_case = GetCorrelationData(db=self.SQLAlchemy)

    def getCorrelationData(self, days: int, user_id: int):
        try:
            data = self.use_case.run(user_id, days)
            return jsonify({
                "status": True,
                "data": {
                    "type": "correlation",
                    "chart_type": "scatter",
                    "attributes": {
                        "days_analyzed": days,
                        "points": data
                    }
                }
            }), 200
        except Exception as e:
            return jsonify({"status": False, "error": str(e)}), 500
