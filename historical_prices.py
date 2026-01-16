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


engine = create_engine(
    f'postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}'
)
Session = sessionmaker(bind=engine)


def check_cache(ticker, multiplier, timespan, from_date, to_date):

    session = Session()
    try:
        request = session.query(RequestParams).filter_by(
            ticker=ticker,
            multiplier=multiplier,
            timespan=timespan,
            from_date=from_date,
            to_date=to_date
        ).first()
        
        if request:
            results = session.query(HistPricesResults).filter_by(
                request_id=request.id
            ).all()
            
            if results:
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

    session = Session()
    try:
        request_params = RequestParams(
            ticker=ticker,
            multiplier=multiplier,
            timespan=timespan,
            from_date=from_date,
            to_date=to_date
        )
        session.add(request_params)
        session.flush()
        
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

    print("🔍 Verificando caché...")
    cached_data = check_cache(ticker, multiplier, timespan, from_date, to_date)
    
    if cached_data is not None:
        print("✅ Datos encontrados en caché!")
        return cached_data
    
    print("📡 Consultando API de Polygon.io...")
    
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
            df = pd.DataFrame(data['results'])
            
            df['timestamp'] = pd.to_datetime(df['t'], unit='ms')
            
            df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert('US/Eastern')
            
            df = df.rename(columns={
                'v': 'volume',
                'o': 'open',
                'c': 'close',
                'h': 'high',
                'l': 'low'
            })
            
            df = df[['timestamp', 'volume', 'open', 'close', 'high', 'low']]
            df.set_index('timestamp', inplace=True)
            
            save_to_cache(ticker, multiplier, timespan, from_date, to_date, df)
            
            return df
        else:
            print(f"⚠️ No se encontraron datos: {data.get('status')}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en la solicitud: {e}")
        return None


def generate_chart(df, ticker, chart_type='candle', output_path='periodic_historical_fig/chart.png'):

    try:
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
        
        plot_df = df.copy()
        plot_df.columns = [col.capitalize() for col in plot_df.columns]
        
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

    df = fetch_historical_prices(ticker, multiplier, timespan, from_date, to_date)
    
    if df is None or df.empty:
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f'periodic_historical_fig/{ticker}_{timestamp}.png'
    
    chart_path = generate_chart(df, ticker, chart_type, output_path)
    
    return chart_path


if __name__ == "__main__":
    pass  # Eliminar ejecución hardcodeada
