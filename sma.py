import requests
import pandas as pd
from datetime import datetime, timedelta
from config import api_key


def calculate_sma(data, period):
    if len(data) < period:
        return None
    
    return data[-period:].mean()


def fetch_daily_prices(ticker, days=250):
    to_date = datetime.now() - timedelta(days=1)  # Datos de hace 3 días
    from_date = to_date - timedelta(days=days + 150)  # Extra días para compensar fines de semana
    
    from_str = from_date.strftime('%Y-%m-%d')
    to_str = to_date.strftime('%Y-%m-%d')
    
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{from_str}/{to_str}"
    
    params = {
        'adjusted': 'true',
        'sort': 'asc',
        'limit': 50000,  # Máximo permitido
        'apiKey': api_key
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        print(f"📡 API Response status: {data.get('status')}")
        print(f"📊 Results count: {len(data.get('results', []))}")
        
        if data.get('status') == 'OK' and 'results' in data and len(data['results']) > 0:
            df = pd.DataFrame(data['results'])
            df['date'] = pd.to_datetime(df['t'], unit='ms')
            df = df.rename(columns={
                'c': 'close',
                'o': 'open',
                'h': 'high',
                'l': 'low',
                'v': 'volume'
            })
            df = df[['date', 'close', 'open', 'high', 'low', 'volume']]
            df.set_index('date', inplace=True)
            df = df.sort_index()
            
            return df
        else:
            print(f"⚠️ No se encontraron datos: {data.get('status')}")
            print(f"⚠️ Message: {data.get('message', 'No message')}")
            print(f"⚠️ Full response: {data}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en la solicitud: {e}")
        return None


def analyze_sma(ticker):
    print(f"📊 Analizando SMA para {ticker}...")
    
    df = fetch_daily_prices(ticker, days=250)
    #print(df)  # Mostrar el DataFrame obtenido
    
    if df is None or df.empty:
        return None
    
    if len(df) < 200:
        return {
            'error': f'No hay suficientes datos para calcular SMA 200 (solo {len(df)} días disponibles)'
        }
    
    close_prices = df['close']

    sma_200 = calculate_sma(close_prices, 200)
    sma_50 = calculate_sma(close_prices, 50) if len(df) >= 50 else None
    
    print(sma_200, sma_50)  # Mostrar los valores calculados

    current_price = close_prices.iloc[-1]
    last_date = df.index[-1]
    first_date = df.index[0]
    
    if sma_50 is None:
        trend = "Insuficientes datos para SMA 50"
        signal = "⚠️"
    elif sma_50 > sma_200:
        trend = "ALCISTA (Bullish)"
        signal = "🟢"
        trend_description = "La SMA 50 está por encima de la SMA 200, lo que indica una tendencia alcista."
    elif sma_50 < sma_200:
        trend = "BAJISTA (Bearish)"
        signal = "🔴"
        trend_description = "La SMA 50 está por debajo de la SMA 200, lo que indica una tendencia bajista."
    else:
        trend = "CRUCE (Crossover)"
        signal = "🟡"
        trend_description = "Las SMA 50 y SMA 200 están en el mismo nivel. Posible cambio de tendencia."
    
    sma_200_pct = ((current_price - sma_200) / sma_200) * 100
    sma_50_pct = ((current_price - sma_50) / sma_50) * 100 if sma_50 else 0
    
    result = {
        'ticker': ticker,
        'current_price': current_price,
        'first_date': first_date.strftime('%Y-%m-%d'),
        'last_date': last_date.strftime('%Y-%m-%d'),
        'sma_200': sma_200,
        'sma_50': sma_50,
        'trend': trend,
        'signal': signal,
        'trend_description': trend_description if sma_50 else "",
        'price_vs_sma200': sma_200_pct,
        'price_vs_sma50': sma_50_pct,
        'total_days': len(df)
    }
    
    return result


def format_sma_result(result):
    if result is None:
        return "❌ No se pudieron obtener datos para el análisis."
    
    if 'error' in result:
        return f"❌ Error: {result['error']}"
    
    message = f"""
📊 **ANÁLISIS SMA - {result['ticker']}**

**Información General:**
📅 Fechas calculadas: {result['first_date']} - {result['last_date']}
💰 Precio Actual: ${result['current_price']:.2f}
📈 Total de días analizados: {result['total_days']}

**Medias Móviles:**
📉 SMA 200 días: ${result['sma_200']:.2f}
   → Precio vs SMA200: {result['price_vs_sma200']:+.2f}%

📊 SMA 50 días: ${result['sma_50']:.2f}
   → Precio vs SMA50: {result['price_vs_sma50']:+.2f}%

**Análisis de Tendencia:**
{result['signal']} **{result['trend']}**

{result['trend_description']}

**Interpretación:**
• Cuando SMA50 > SMA200 → Señal ALCISTA 🟢
• Cuando SMA50 < SMA200 → Señal BAJISTA 🔴
• Cuando SMA50 = SMA200 → Posible CRUCE 🟡

⚠️ **Nota:** Este análisis es solo informativo. No es asesoramiento financiero.
"""
    
    return message


def get_sma_analysis(ticker):
    result = analyze_sma(ticker)
    return format_sma_result(result)


if __name__ == "__main__":
    analysis = get_sma_analysis('AAPL')
    print(analysis)
