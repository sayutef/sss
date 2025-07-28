from flask import jsonify
from graphics.application.useCases.getBarrasData_useCase import GetBarChartData
from graphics.infrastructure.dependences import getSQLAlchemy

class BarChartController:
    def __init__(self):
        self.SQLAlchemy = getSQLAlchemy()
        self.use_case = GetBarChartData(db=self.SQLAlchemy)

    def getBarChartData(self, days: int, user_id: int):
        try:
            data = self.use_case.run(user_id, days)
            return jsonify({
                "status": True,
                "data": {
                    "type": "work_hours",
                    "chart_type": "bar",
                    "attributes": {
                        "days_analyzed": days,
                        "data": data
                    }
                }
            }), 200
        except Exception as e:
            return jsonify({"status": False, "error": str(e)}), 500
