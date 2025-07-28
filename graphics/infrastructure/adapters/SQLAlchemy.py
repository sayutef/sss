from database.conn.connection import SessionLocal
from graphics.domain.repositories.graphics_repository import IGraphics
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

class graphicsSQLAlchemy(IGraphics):
    def __init__(self):
        self.session = None
    
    def _get_session(self):
        if self.session:
            try:
                self.session.close()
            except:
                pass
        self.session = SessionLocal()
        return self.session
    
    def _close_session(self):
        if self.session:
            try:
                self.session.close()
            except:
                pass
            finally:
                self.session = None
    
    def get_user_prototype_id(self, user_id: int) -> str:
        session = self._get_session()
        try:
            query = text("""
                SELECT prototype_id 
                FROM prototypes 
                WHERE user_id = :user_id
                LIMIT 1
            """)
            result = session.execute(query, {"user_id": user_id}).fetchone()
            if not result:
                raise ValueError(f"No se encontró prototype_id para user_id={user_id}")
            return result[0]
        except SQLAlchemyError as e:
            session.rollback()
            raise RuntimeError(f"Error SQLAlchemy al obtener prototype_id: {e}") from e
        except Exception as e:
            session.rollback()
            raise RuntimeError(f"Error inesperado al obtener prototype_id: {e}") from e
        finally:
            self._close_session()

    def get_waste_types_distribution(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        session = self._get_session()
        try:
            prototype_id = self.get_user_prototype_id(user_id)
            query = text("""
                SELECT 
                    wt.waste_type,
                    COUNT(wc.waste_collection_id) as count,
                    SUM(wc.amount) as total_amount
                FROM waste_collection wc
                JOIN waste_types wt ON wc.waste_id = wt.waste_id
                WHERE wc.prototype_id = :prototype_id
                GROUP BY wt.waste_type
                ORDER BY total_amount DESC
            """)
            result = session.execute(query, {"prototype_id": prototype_id}).fetchall()
            if not result:
                raise ValueError(f"No se encontraron datos de tipos de residuos para prototype_id={prototype_id}")
            return [
                {
                    "waste_type": row[0],
                    "count": row[1],
                    "total_amount": float(row[2]) if row[2] else 0
                }
                for row in result
            ]
        except SQLAlchemyError as e:
            session.rollback()
            raise RuntimeError(f"Error SQLAlchemy al obtener distribución de residuos: {e}") from e
        except Exception as e:
            session.rollback()
            raise RuntimeError(f"Error inesperado al obtener distribución de residuos: {e}") from e
        finally:
            self._close_session()

    def get_weight_periods_data(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        session = self._get_session()
        try:
            prototype_id = self.get_user_prototype_id(user_id)
            date_limit = datetime.now() - timedelta(days=days)
            query = text("""
                SELECT 
                    wp.period_id,
                    wp.start_hour,
                    wp.end_hour,
                    wp.day_work,
                    AVG(wd.weight) as avg_weight,
                    COUNT(wd.weight_data_id) as readings_count
                FROM work_periods wp
                LEFT JOIN weight_data wd ON wp.period_id = wd.period_id
                WHERE wp.prototype_id = :prototype_id 
                    AND wp.start_hour >= :date_limit
                GROUP BY wp.period_id, wp.start_hour, wp.end_hour, wp.day_work
                ORDER BY wp.start_hour DESC
            """)
            result = session.execute(query, {
                "prototype_id": prototype_id,
                "date_limit": date_limit
            }).fetchall()
            if not result:
                raise ValueError(f"No se encontraron datos de peso por períodos para prototype_id={prototype_id} desde {date_limit}")
            return [
                {
                    "period_id": row[0],
                    "start_hour": row[1].isoformat() if row[1] else None,
                    "end_hour": row[2].isoformat() if row[2] else None,
                    "day_work": row[3],
                    "avg_weight": float(row[4]) if row[4] else 0,
                    "readings_count": row[5]
                }
                for row in result
            ]
        except SQLAlchemyError as e:
            session.rollback()
            raise RuntimeError(f"Error SQLAlchemy al obtener datos de peso por períodos: {e}") from e
        except Exception as e:
            session.rollback()
            raise RuntimeError(f"Error inesperado al obtener datos de peso por períodos: {e}") from e
        finally:
            self._close_session()

    def get_distance_cumulative_data(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        session = self._get_session()
        try:
            prototype_id = self.get_user_prototype_id(user_id)
            date_limit = datetime.now() - timedelta(days=days)
            query = text("""
                SELECT 
                    r.period_id,
                    r.distance_traveled,
                    r.weight_waste,
                    wp.start_hour,
                    SUM(r.distance_traveled) OVER (
                        ORDER BY wp.start_hour 
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                    ) as cumulative_distance
                FROM readings r
                JOIN work_periods wp ON r.period_id = wp.period_id
                WHERE r.prototype_id = :prototype_id 
                    AND wp.start_hour >= :date_limit
                ORDER BY wp.start_hour
            """)
            result = session.execute(query, {
                "prototype_id": prototype_id,
                "date_limit": date_limit
            }).fetchall()
            if not result:
                raise ValueError(f"No se encontraron datos de distancia acumulativa para prototype_id={prototype_id} desde {date_limit}")
            return [
                {
                    "period_id": row[0],
                    "distance_traveled": float(row[1]) if row[1] else 0,
                    "weight_waste": float(row[2]) if row[2] else 0,
                    "start_hour": row[3].isoformat() if row[3] else None,
                    "cumulative_distance": float(row[4]) if row[4] else 0
                }
                for row in result
            ]
        except SQLAlchemyError as e:
            session.rollback()
            raise RuntimeError(f"Error SQLAlchemy al obtener datos de distancia acumulativa: {e}") from e
        except Exception as e:
            session.rollback()
            raise RuntimeError(f"Error inesperado al obtener datos de distancia acumulativa: {e}") from e
        finally:
            self._close_session()

    def get_gps_speed_analysis(self, user_id: int, days: int = 7) -> List[Dict[str, Any]]:
        session = self._get_session()
        try:
            prototype_id = self.get_user_prototype_id(user_id)
            date_limit = datetime.now() - timedelta(days=days)
            query = text("""
                SELECT 
                    AVG(speed) as avg_speed,
                    MAX(speed) as max_speed,
                    MIN(speed) as min_speed,
                    COUNT(*) as total_readings,
                    DATE(date_gps) as date
                FROM gps_data 
                WHERE prototype_id = :prototype_id 
                    AND date_gps >= :date_limit
                GROUP BY DATE(date_gps)
                ORDER BY date DESC
            """)
            result = session.execute(query, {
                "prototype_id": prototype_id,
                "date_limit": date_limit
            }).fetchall()
            if not result:
                raise ValueError(f"No se encontraron datos de análisis GPS para prototype_id={prototype_id} desde {date_limit}")
            return [
                {
                    "avg_speed": float(row[0]) if row[0] else 0,
                    "max_speed": float(row[1]) if row[1] else 0,
                    "min_speed": float(row[2]) if row[2] else 0,
                    "total_readings": row[3],
                    "date": row[4].isoformat() if row[4] else None
                }
                for row in result
            ]
        except SQLAlchemyError as e:
            session.rollback()
            raise RuntimeError(f"Error SQLAlchemy al obtener análisis de velocidad GPS: {e}") from e
        except Exception as e:
            session.rollback()
            raise RuntimeError(f"Error inesperado al obtener análisis de velocidad GPS: {e}") from e
        finally:
            self._close_session()

    def get_bar_chart_data(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        session = self._get_session()
        try:
            prototype_id = self.get_user_prototype_id(user_id)
            date_limit = datetime.now() - timedelta(days=days)
            query = text("""
                SELECT 
                    EXTRACT(DOW FROM wp.start_hour) AS day_of_week,
                    EXTRACT(HOUR FROM wd.hour_period) AS hour,
                    AVG(wd.weight) AS avg_weight
                FROM work_periods wp
                JOIN weight_data wd ON wp.period_id = wd.period_id
                WHERE wp.prototype_id = :prototype_id
                    AND wp.start_hour >= :date_limit
                GROUP BY day_of_week, hour
                ORDER BY day_of_week, hour
            """)
            result = session.execute(query, {
                "prototype_id": prototype_id,
                "date_limit": date_limit
            }).fetchall()
            if not result:
                raise ValueError(f"No se encontraron datos para gráfica de barras para prototype_id={prototype_id} desde {date_limit}")
            return [
                {
                    "day_of_week": int(row[0]),
                    "hour": int(row[1]),
                    "avg_weight": float(row[2]) if row[2] else 0
                }
                for row in result
            ]
        except SQLAlchemyError as e:
            session.rollback()
            raise RuntimeError(f"Error SQLAlchemy al obtener datos de barras: {e}") from e
        except Exception as e:
            session.rollback()
            raise RuntimeError(f"Error inesperado al obtener datos de barras: {e}") from e
        finally:
            self._close_session()

    def get_correlation_data(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        session = self._get_session()
        try:
            prototype_id = self.get_user_prototype_id(user_id)
            date_limit = datetime.now() - timedelta(days=days)
            query = text("""
                SELECT 
                    r.distance_traveled,
                    r.weight_waste,
                    wp.start_hour
                FROM readings r
                JOIN work_periods wp ON r.period_id = wp.period_id
                WHERE wp.prototype_id = :prototype_id
                    AND wp.start_hour >= :date_limit
            """)
            result = session.execute(query, {
                "prototype_id": prototype_id,
                "date_limit": date_limit
            }).fetchall()
            if not result:
                raise ValueError(f"No se encontraron datos para gráfica de correlación para prototype_id={prototype_id} desde {date_limit}")
            return [
                {
                    "distance_traveled": float(row[0]) if row[0] else 0,
                    "weight_waste": float(row[1]) if row[1] else 0,
                    "start_hour": row[2].isoformat() if row[2] else None
                }
                for row in result
            ]
        except SQLAlchemyError as e:
            session.rollback()
            raise RuntimeError(f"Error SQLAlchemy al obtener datos de correlación: {e}") from e
        except Exception as e:
            session.rollback()
            raise RuntimeError(f"Error inesperado al obtener datos de correlación: {e}") from e
        finally:
            self._close_session()

    def get_probability_data(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        session = self._get_session()
        try:
            prototype_id = self.get_user_prototype_id(user_id)
            date_limit = datetime.now() - timedelta(days=days)
            query = text("""
                SELECT 
                    DATE(wp.start_hour) AS day,
                    SUM(r.weight_waste) AS total_weight
                FROM readings r
                JOIN work_periods wp ON r.period_id = wp.period_id
                WHERE wp.prototype_id = :prototype_id
                    AND wp.start_hour >= :date_limit
                GROUP BY day
                ORDER BY day
            """)
            result = session.execute(query, {
                "prototype_id": prototype_id,
                "date_limit": date_limit
            }).fetchall()
            if not result:
                raise ValueError(f"No se encontraron datos para gráfica de probabilidad para prototype_id={prototype_id} desde {date_limit}")

            total_weight = sum(float(row[1]) for row in result if row[1])
            cumulative = 0
            data = []
            for row in result:
                daily_weight = float(row[1]) if row[1] else 0
                cumulative += daily_weight
                probability = (cumulative / total_weight) * 100 if total_weight else 0
                data.append({
                    "day": row[0].isoformat(),
                    "daily_weight": daily_weight,
                    "cumulative_weight": cumulative,
                    "probability_percent": round(probability, 2)
                })
            return data
        except SQLAlchemyError as e:
            session.rollback()
            raise RuntimeError(f"Error SQLAlchemy al obtener datos de probabilidad: {e}") from e
        except Exception as e:
            session.rollback()
            raise RuntimeError(f"Error inesperado al obtener datos de probabilidad: {e}") from e
        finally:
            self._close_session()

    def __del__(self):
        self._close_session()
