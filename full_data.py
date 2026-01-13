

import requests
from datetime import datetime, timedelta
from config import api_key
from utils import format_price, format_large_number


def fetch_ticker_details(ticker):

    url = f"https://api.polygon.io/v3/reference/tickers/{ticker}"
    
    params = {
        'apiKey': api_key
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('status') == 'OK' and 'results' in data:
            return data['results']
        else:
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al obtener detalles: {e}")
        return None


def fetch_latest_quote(ticker):

    # Obtener último día de trading - usar datos de hace unos días para evitar problemas con plan gratuito
    to_date = datetime.now() - timedelta(days=3)  # Datos de hace 3 días
    from_date = to_date - timedelta(days=10)  # Últimos 10 días para asegurar que obtenemos datos
    
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{from_date.strftime('%Y-%m-%d')}/{to_date.strftime('%Y-%m-%d')}"
    
    params = {
        'adjusted': 'true',
        'sort': 'desc',
        'limit': 1,
        'apiKey': api_key
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        print(f"📡 Full Data API Response status: {data.get('status')}")
        print(f"📊 Full Data Results count: {len(data.get('results', []))}")
        
        if data.get('status') == 'OK' and 'results' in data and len(data['results']) > 0:
            return data['results'][0]
        else:
            print(f"⚠️ Full Data - No data: {data.get('status')}")
            print(f"⚠️ Full Data - Message: {data.get('message', 'No message')}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al obtener cotización: {e}")
        return None


def get_full_data(ticker):

    print(f"📋 Obteniendo datos completos para {ticker}...")
    
    # Obtener detalles del ticker
    details = fetch_ticker_details(ticker)
    
    # Obtener última cotización
    quote = fetch_latest_quote(ticker)
    
    if quote is None:
        return f"❌ No se pudieron obtener datos para {ticker}. Verifica que el ticker sea válido."
    
    # Extraer datos de la cotización
    timestamp = datetime.fromtimestamp(quote['t'] / 1000)
    open_price = quote.get('o', 0)
    high_price = quote.get('h', 0)
    low_price = quote.get('l', 0)
    close_price = quote.get('c', 0)
    volume = quote.get('v', 0)
    
    # Calcular cambio porcentual del día
    if open_price > 0:
        day_change = ((close_price - open_price) / open_price) * 100
        change_emoji = "🟢" if day_change >= 0 else "🔴"
    else:
        day_change = 0
        change_emoji = "⚪"
    
    # Construir mensaje
    message = f"""
📋 **INFORMACIÓN COMPLETA - {ticker.upper()}**

**Última Actualización:**
📅 Fecha: {timestamp.strftime('%Y-%m-%d')}
🕐 Hora: {timestamp.strftime('%H:%M:%S')} UTC

**Precios del Día:**
💰 Precio de Cierre: {format_price(close_price)}
📊 Precio de Apertura: {format_price(open_price)}
📈 Precio Máximo: {format_price(high_price)}
📉 Precio Mínimo: {format_price(low_price)}

**Cambio del Día:**
{change_emoji} {day_change:+.2f}% ({format_price(close_price - open_price)})

**Volumen:**
📊 Volumen: {format_large_number(volume)} acciones

**Rango del Día:**
↕️ {format_price(low_price)} - {format_price(high_price)}
   Amplitud: {format_price(high_price - low_price)} ({((high_price - low_price) / low_price * 100):.2f}%)
"""
    
    # Agregar información adicional del ticker si está disponible
    if details:
        market = details.get('market', 'N/A')
        locale = details.get('locale', 'N/A')
        primary_exchange = details.get('primary_exchange', 'N/A')
        currency = details.get('currency_name', 'N/A')
        
        message += f"""
**Información del Ticker:**
🏢 Mercado: {market}
🌍 Localización: {locale}
🏦 Bolsa Principal: {primary_exchange}
💵 Moneda: {currency}
"""
        
        # Agregar nombre de la compañía si está disponible
        if 'name' in details:
            message += f"\n**Compañía:** {details['name']}\n"
    
    message += "\n⚠️ **Nota:** Los datos mostrados son del último día de trading disponible (pueden tener retraso de unos días)."
    
    return message


if __name__ == "__main__":
    # Ejemplo de uso
    data = get_full_data('AAPL')
    print(data)
