"""
Script para crear las tablas necesarias en PostgreSQL
Debe ejecutarse después de crear la base de datos con postgres_create_db.py
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from config import postgres_user, postgres_password, postgres_host, postgres_port, postgres_db

# Crear Base para los modelos
Base = declarative_base()


class RequestParams(Base):
    """
    Tabla para almacenar parámetros de solicitudes de precios históricos
    """
    __tablename__ = 'request_params'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), nullable=False)
    multiplier = Column(Integer, nullable=False)
    timespan = Column(String(10), nullable=False)
    from_date = Column(String(10), nullable=False)
    to_date = Column(String(10), nullable=False)
    
    # Relación con hist_prices_results
    results = relationship("HistPricesResults", back_populates="request")
    
    def __repr__(self):
        return f"<RequestParams(ticker={self.ticker}, from={self.from_date}, to={self.to_date})>"


class HistPricesResults(Base):
    """
    Tabla para almacenar resultados de precios históricos
    """
    __tablename__ = 'hist_prices_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(Integer, ForeignKey('request_params.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    volume = Column(Float, nullable=False)
    open = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    
    # Relación con request_params
    request = relationship("RequestParams", back_populates="results")
    
    def __repr__(self):
        return f"<HistPricesResults(timestamp={self.timestamp}, close={self.close})>"


def create_tables():
    """Crea todas las tablas en la base de datos"""
    try:
        # Crear motor de conexión a PostgreSQL
        engine = create_engine(
            f'postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}'
        )
        
        # Crear todas las tablas definidas
        Base.metadata.create_all(engine)
        
        print("✅ Tablas creadas exitosamente:")
        print("   - request_params")
        print("   - hist_prices_results")
        
    except Exception as error:
        print(f"❌ Error al crear las tablas: {error}")


if __name__ == "__main__":
    print("🔧 Iniciando creación de tablas...")
    create_tables()
    print("✅ Proceso completado!")
