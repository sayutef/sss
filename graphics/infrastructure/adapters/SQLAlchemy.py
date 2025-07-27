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
        """Crea una nueva sesión para cada operación"""
        if self.session:
            try:
                self.session.close()
            except:
                pass
        self.session = SessionLocal()
        return self.session
    
    def _close_session(self):
        """Cierra la sesión actual"""
        if self.session:
            try:
                self.session.close()
            except:
                pass
            finally:
                self.session = None
    
    def get_user_prototype_id(self, user_id: int) -> str:
        """Obtiene el prototype_id del usuario"""
        session = self._get_session()
        try:
            query = text("""
                SELECT prototype_id 
                FROM prototypes 
                WHERE user_id = :user_id
                LIMIT 1
            """)
            result = session.execute(query, {"user_id": user_id}).fetchone()
            return result[0] if result else None
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error al obtener prototype_id: {e}")
            raise e
        except Exception as e:
            session.rollback()
            print(f"Error inesperado al obtener prototype_id: {e}")
            raise e
        finally:
            self._close_session()
    
    def get_waste_types_distribution(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Obtiene la distribución de tipos de residuos para gráfico de pastel"""
        session = self._get_session()
        try:
            prototype_id = self.get_user_prototype_id(user_id)
            print(f"🔍 DEBUG - user_id: {user_id}, prototype_id: {prototype_id}")
            
            if not prototype_id:
                print("❌ No se encontró prototype_id")
                return []
            
            # Query simplificada sin restricciones de fecha
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
            print(f"🔍 DEBUG - Query result: {result}")
            
            if not result:
                print("⚠️ No hay datos en la BASE DE DATOS")
                return []
            
            data = [
                {
                    "waste_type": row[0],
                    "count": row[1],
                    "total_amount": float(row[2]) if row[2] else 0
                }
                for row in result
            ]
            print(f"✅ Retornando datos reales: {data}")
            return data
            
        except SQLAlchemyError as e:
            session.rollback()
            print(f"❌ SQLAlchemy ERROR: {e}")
            return []
        except Exception as e:
            session.rollback()
            print(f"❌ General ERROR: {e}")
            return []
        finally:
            self._close_session()
    
    def get_weight_periods_data(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Obtiene datos de peso por períodos para gráfico de anillo"""
        session = self._get_session()
        try:
            prototype_id = self.get_user_prototype_id(user_id)
            if not prototype_id:
                return []
            
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
            print(f"Error al obtener datos de peso por períodos: {e}")
            return []
        except Exception as e:
            session.rollback()
            print(f"Error inesperado al obtener datos de peso por períodos: {e}")
            return []
        finally:
            self._close_session()
    
    def get_distance_cumulative_data(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Obtiene datos de distancia acumulativa para gráfico ojiva"""
        session = self._get_session()
        try:
            prototype_id = self.get_user_prototype_id(user_id)
            if not prototype_id:
                return []
            
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
            print(f"Error al obtener datos de distancia acumulativa: {e}")
            return []
        except Exception as e:
            session.rollback()
            print(f"Error inesperado al obtener datos de distancia acumulativa: {e}")
            return []
        finally:
            self._close_session()
    
    def get_gps_speed_analysis(self, user_id: int, days: int = 7) -> List[Dict[str, Any]]:
        """Obtiene análisis de velocidad GPS"""
        session = self._get_session()
        try:
            prototype_id = self.get_user_prototype_id(user_id)
            if not prototype_id:
                return []
            
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
            print(f"Error al obtener análisis de velocidad GPS: {e}")
            return []
        except Exception as e:
            session.rollback()
            print(f"Error inesperado al obtener análisis de velocidad GPS: {e}")
            return []
        finally:
            self._close_session()
    
    def __del__(self):
        """Asegurar que la sesión se cierra al destruir el objeto"""
        self._close_session()
        
    def get_bar_chart_data(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Obtiene datos para la gráfica de barras (peso promedio por día de la semana y hora)"""
        session = self._get_session()
        try:
            prototype_id = self.get_user_prototype_id(user_id)
            if not prototype_id:
                return []

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
            print(f"Error al obtener datos de barras: {e}")
            return []
        except Exception as e:
            session.rollback()
            print(f"Error inesperado al obtener datos de barras: {e}")
            return []
        finally:
            self._close_session()

    def get_correlation_data(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Obtiene datos para la gráfica de correlación (distancia vs peso)"""
        session = self._get_session()
        try:
            prototype_id = self.get_user_prototype_id(user_id)
            if not prototype_id:
                return []

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
            print(f"Error al obtener datos de correlación: {e}")
            return []
        except Exception as e:
            session.rollback()
            print(f"Error inesperado al obtener datos de correlación: {e}")
            return []
        finally:
            self._close_session()

    def get_probability_data(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Obtiene datos acumulativos de peso para gráfica de ojiva (probabilidad)"""
        session = self._get_session()
        try:
            prototype_id = self.get_user_prototype_id(user_id)
            if not prototype_id:
                return []

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

            # Calculamos acumulado y porcentaje
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
            print(f"Error al obtener datos de probabilidad: {e}")
            return []
        except Exception as e:
            session.rollback()
            print(f"Error inesperado al obtener datos de probabilidad: {e}")
            return []
        finally:
            self._close_session()
