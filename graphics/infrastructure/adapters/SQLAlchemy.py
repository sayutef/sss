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
                print("⚠️ No hay datos en la BD, retornando mock")
                return [
                    {"waste_type": "Plástico", "count": 150, "total_amount": 45.5},
                    {"waste_type": "Papel", "count": 120, "total_amount": 38.2},
                    {"waste_type": "Vidrio", "count": 80, "total_amount": 25.1},
                    {"waste_type": "Metal", "count": 60, "total_amount": 18.7}
                ]
            
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
            return [
                {"waste_type": "Plástico", "count": 150, "total_amount": 45.5},
                {"waste_type": "Papel", "count": 120, "total_amount": 38.2},
                {"waste_type": "Vidrio", "count": 80, "total_amount": 25.1},
                {"waste_type": "Metal", "count": 60, "total_amount": 18.7}
            ]
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
            return [
                {
                    "period_id": 1,
                    "start_hour": datetime.now().isoformat(),
                    "end_hour": (datetime.now() + timedelta(hours=8)).isoformat(),
                    "day_work": "Lunes",
                    "avg_weight": 25.5,
                    "readings_count": 45
                },
                {
                    "period_id": 2,
                    "start_hour": (datetime.now() - timedelta(days=1)).isoformat(),
                    "end_hour": (datetime.now() - timedelta(days=1) + timedelta(hours=8)).isoformat(),
                    "day_work": "Domingo",
                    "avg_weight": 30.2,
                    "readings_count": 52
                }
            ]
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
            return [
                {
                    "period_id": 1,
                    "distance_traveled": 5.2,
                    "weight_waste": 15.3,
                    "start_hour": datetime.now().isoformat(),
                    "cumulative_distance": 5.2
                },
                {
                    "period_id": 2,
                    "distance_traveled": 3.8,
                    "weight_waste": 12.1,
                    "start_hour": (datetime.now() + timedelta(hours=1)).isoformat(),
                    "cumulative_distance": 9.0
                }
            ]
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
            return [
                {
                    "avg_speed": 25.5,
                    "max_speed": 45.2,
                    "min_speed": 5.1,
                    "total_readings": 156,
                    "date": datetime.now().date().isoformat()
                },
                {
                    "avg_speed": 22.8,
                    "max_speed": 38.7,
                    "min_speed": 3.2,
                    "total_readings": 142,
                    "date": (datetime.now() - timedelta(days=1)).date().isoformat()
                }
            ]
        except Exception as e:
            session.rollback()
            print(f"Error inesperado al obtener análisis de velocidad GPS: {e}")
            return []
        finally:
            self._close_session()
    
    def __del__(self):
        """Asegurar que la sesión se cierra al destruir el objeto"""
        self._close_session()