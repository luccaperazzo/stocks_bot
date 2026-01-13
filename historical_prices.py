"""
Módulo para obtener precios históricos de acciones
Incluye integración con API de Polygon.io y caché en PostgreSQL
"""

import os
import requests
import pandas as pd
import mplfinance as mpf
from datetime import datetime
import pytz
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from postgres_create_table import RequestParams, HistPricesResults
from config import api_key, postgres_user, postgres_password, postgres_host, postgres_port, postgres_db


# Crear motor de base de datos
engine = create_engine(
    f'postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}'
)
Session = sessionmaker(bind=engine)


def check_cache(ticker, multiplier, timespan, from_date, to_date):
    """
    Verifica si los datos ya existen en la caché de PostgreSQL
    
    Returns:
        pandas.DataFrame o None si no hay datos en caché
    """
    session = Session()
    try:
        # Buscar parámetros de solicitud coincidentes
        request = session.query(RequestParams).filter_by(
            ticker=ticker,
            multiplier=multiplier,
            timespan=timespan,
            from_date=from_date,
            to_date=to_date
        ).first()
        
        if request:
            # Si existe, obtener los resultados
            results = session.query(HistPricesResults).filter_by(
                request_id=request.id
            ).all()
            
            if results:
                # Convertir a DataFrame
                data = []
                for result in results:
                    data.append({
                        'timestamp': result.timestamp,
                        'volume': result.volume,
                        'open': result.open,
                        'close': result.close,
                        'high': result.high,
                        'low': result.low
                    })
                
                df = pd.DataFrame(data)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True)
                
                return df
        
        return None
        
    except Exception as e:
        print(f"Error al verificar caché: {e}")
        return None
    finally:
        session.close()


def save_to_cache(ticker, multiplier, timespan, from_date, to_date, df):
    """
    Guarda los resultados en la caché de PostgreSQL
    """
    session = Session()
    try:
        # Crear nuevo registro de parámetros
        request_params = RequestParams(
            ticker=ticker,
            multiplier=multiplier,
            timespan=timespan,
            from_date=from_date,
            to_date=to_date
        )
        session.add(request_params)
        session.flush()  # Para obtener el ID
        
        # Guardar resultados
        for index, row in df.iterrows():
            result = HistPricesResults(
                request_id=request_params.id,
                timestamp=index.to_pydatetime(),
                volume=float(row['volume']),
                open=float(row['open']),
                close=float(row['close']),
                high=float(row['high']),
                low=float(row['low'])
            )
            session.add(result)
        
        session.commit()
        print("✅ Datos guardados en caché")
        
    except Exception as e:
        session.rollback()
        print(f"Error al guardar en caché: {e}")
    finally:
        session.close()


def fetch_historical_prices(ticker, multiplier, timespan, from_date, to_date):
    """
    Obtiene precios históricos desde la API de Polygon.io
    
    Args:
        ticker: Símbolo de la acción (ej: AAPL)
        multiplier: Multiplicador de tiempo
        timespan: Periodo (day, week, month, etc.)
        from_date: Fecha inicial (YYYY-MM-DD)
        to_date: Fecha final (YYYY-MM-DD)
    
    Returns:
        pandas.DataFrame con los datos históricos
    """
    # Primero verificar caché
    print("🔍 Verificando caché...")
    cached_data = check_cache(ticker, multiplier, timespan, from_date, to_date)
    
    if cached_data is not None:
        print("✅ Datos encontrados en caché!")
        return cached_data
    
    print("📡 Consultando API de Polygon.io...")
    
    # Construir URL de la API
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}"
    
    params = {
        'adjusted': 'true',
        'sort': 'asc',
        'apiKey': api_key
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('status') == 'OK' and 'results' in data:
            # Convertir a DataFrame
            df = pd.DataFrame(data['results'])
            
            # Convertir timestamp (milisegundos) a datetime
            df['timestamp'] = pd.to_datetime(df['t'], unit='ms')
            
            # Convertir de UTC a EST
            df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert('US/Eastern')
            
            # Renombrar columnas
            df = df.rename(columns={
                'v': 'volume',
                'o': 'open',
                'c': 'close',
                'h': 'high',
                'l': 'low'
            })
            
            # Seleccionar solo las columnas necesarias
            df = df[['timestamp', 'volume', 'open', 'close', 'high', 'low']]
            df.set_index('timestamp', inplace=True)
            
            # Guardar en caché
            save_to_cache(ticker, multiplier, timespan, from_date, to_date, df)
            
            return df
        else:
            print(f"⚠️ No se encontraron datos: {data.get('status')}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en la solicitud: {e}")
        return None


def generate_chart(df, ticker, chart_type='candle', output_path='periodic_historical_fig/chart.png'):
    """
    Genera un gráfico financiero usando mplfinance
    
    Args:
        df: DataFrame con datos OHLCV
        ticker: Símbolo de la acción
        chart_type: 'candle' o 'line'
        output_path: Ruta donde guardar el gráfico
    
    Returns:
        Ruta del archivo generado o None en caso de error
    """
    try:
        # Configurar el estilo
        mc = mpf.make_marketcolors(
            up='green', down='red',
            edge='inherit',
            wick={'up': 'green', 'down': 'red'},
            volume='in'
        )
        
        s = mpf.make_mpf_style(
            marketcolors=mc,
            gridstyle='-',
            y_on_right=False
        )
        
        # Preparar el DataFrame (mplfinance necesita columnas en mayúsculas)
        plot_df = df.copy()
        plot_df.columns = [col.capitalize() for col in plot_df.columns]
        
        # Crear el gráfico
        if chart_type == 'candle':
            mpf.plot(
                plot_df,
                type='candle',
                style=s,
                volume=True,
                title=f'{ticker} - Historical Prices',
                ylabel='Price (USD)',
                ylabel_lower='Volume',
                savefig=output_path,
                figsize=(12, 8)
            )
        elif chart_type == 'line':
            mpf.plot(
                plot_df,
                type='line',
                style=s,
                volume=True,
                title=f'{ticker} - Historical Prices',
                ylabel='Price (USD)',
                ylabel_lower='Volume',
                savefig=output_path,
                figsize=(12, 8)
            )
        else:
            print(f"❌ Tipo de gráfico inválido: {chart_type}")
            return None
        
        print(f"✅ Gráfico guardado en: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Error al generar gráfico: {e}")
        return None


def get_historical_prices_chart(ticker, multiplier, timespan, from_date, to_date, chart_type='candle'):
    """
    Función principal para obtener precios históricos y generar gráfico
    
    Returns:
        Ruta del archivo de gráfico o None en caso de error
    """
    # Obtener datos
    df = fetch_historical_prices(ticker, multiplier, timespan, from_date, to_date)
    
    if df is None or df.empty:
        return None
    
    # Generar nombre único para el archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f'periodic_historical_fig/{ticker}_{timestamp}.png'
    
    # Generar gráfico
    chart_path = generate_chart(df, ticker, chart_type, output_path)
    
    return chart_path


if __name__ == "__main__":
    # Ejemplo de uso
    chart = get_historical_prices_chart(
        ticker='AAPL',
        multiplier=1,
        timespan='day',
        from_date='2024-01-01',
        to_date='2024-12-31',
        chart_type='candle'
    )
    
    if chart:
        print(f"Gráfico generado: {chart}")
    else:
        print("No se pudo generar el gráfico")
