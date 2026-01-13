

# Mensaje de bienvenida
WELCOME_MESSAGE = """
🤖 **¡Bienvenido al Stocks Bot!**

Soy tu asistente para análisis de acciones estadounidenses. 
Puedo ayudarte con:

📈 **Historical Prices** - Obtén precios históricos con gráficos personalizables
📊 **SMA Analysis** - Calcula medias móviles y analiza tendencias
📋 **Full Data** - Información completa de una acción

Usa /Guide para ver instrucciones detalladas.
"""

# Guía de uso
GUIDE_MESSAGE = """
📖 **GUÍA DE USO**

**📈 HISTORICAL PRICES**
1. Selecciona "📈 Historical Prices"
2. Ingresa el ticker (ej: AAPL, TSLA) - SOLO MAYÚSCULAS
3. Ingresa fecha inicial (formato: YYYY-MM-DD)
4. Ingresa fecha final (formato: YYYY-MM-DD)
5. Ingresa multiplicador de tiempo (número)
6. Selecciona el periodo (day, week, month, etc.) - SOLO MINÚSCULAS
7. Selecciona tipo de gráfico (candle o line) - SOLO MINÚSCULAS

**📊 SMA ANALYSIS**
1. Selecciona "📊 SMA Analysis"
2. Ingresa el ticker de la acción
3. El bot calculará:
   - SMA 200 días
   - SMA 50 días
   - Tendencia del mercado (alcista/bajista)

**Interpretación de SMA:**
🟢 SMA200 < SMA50 → Tendencia ALCISTA
🔴 SMA200 > SMA50 → Tendencia BAJISTA
🟡 SMA200 = SMA50 → CRUCE (Crossover)

**📋 FULL DATA**
Obtiene información completa de precios de una acción.

**⚠️ IMPORTANTE:**
- Los tickers deben estar en MAYÚSCULAS
- Los periodos deben estar en minúsculas
- El formato de fecha es YYYY-MM-DD
- Los datos son del mercado estadounidense
"""

# Mensajes de error
ERROR_INVALID_TICKER = "❌ **Error:** Ticker inválido. Debe estar en MAYÚSCULAS (ej: AAPL, TSLA)"
ERROR_INVALID_DATE = "❌ **Error:** Fecha inválida. Formato correcto: YYYY-MM-DD (ej: 2024-01-01)"
ERROR_INVALID_MULTIPLIER = "❌ **Error:** El multiplicador debe ser un número entero positivo"
ERROR_INVALID_PERIOD = "❌ **Error:** Periodo inválido. Usa: day, week, month, quarter, year (en minúsculas)"
ERROR_INVALID_CHART_TYPE = "❌ **Error:** Tipo de gráfico inválido. Usa: candle o line (en minúsculas)"
ERROR_API_LIMIT = "❌ **Error:** Límite de API alcanzado. Intenta más tarde."
ERROR_NO_DATA = "❌ **Error:** No se encontraron datos para los parámetros especificados."
ERROR_MARKET_CLOSED = "⚠️ **Aviso:** El mercado está cerrado o es día festivo."
ERROR_DATABASE = "❌ **Error:** Error al conectar con la base de datos."

# Mensajes de éxito
SUCCESS_GENERATING_CHART = "⏳ Generando gráfico... Por favor espera."
SUCCESS_CALCULATING_SMA = "⏳ Calculando medias móviles... Por favor espera."
SUCCESS_CHART_GENERATED = "✅ Gráfico generado exitosamente!"
SUCCESS_SMA_CALCULATED = "✅ Análisis SMA completado!"

# Prompts de entrada
PROMPT_TICKER = "Ingresa el ticker de la acción (ej: AAPL, TSLA) - SOLO MAYÚSCULAS:"
PROMPT_START_DATE = "Ingresa la fecha inicial (formato: YYYY-MM-DD):"
PROMPT_END_DATE = "Ingresa la fecha final (formato: YYYY-MM-DD):"
PROMPT_MULTIPLIER = "Ingresa el multiplicador de tiempo (número):"
PROMPT_PERIOD = "Selecciona el periodo:"
PROMPT_CHART_TYPE = "Selecciona el tipo de gráfico:"

# Mensajes de estado
STATUS_FETCHING_DATA = "📡 Obteniendo datos de Polygon.io..."
STATUS_CHECKING_CACHE = "🔍 Verificando caché en base de datos..."
STATUS_CACHE_HIT = "✅ Datos encontrados en caché!"
STATUS_CACHE_MISS = "ℹ️ Datos no encontrados en caché. Consultando API..."


def validate_ticker(ticker: str) -> bool:
  
    return ticker.isupper() and ticker.isalpha() and 1 <= len(ticker) <= 10


def validate_date(date_str: str) -> bool:

    from datetime import datetime
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_multiplier(multiplier_str: str) -> bool:

    try:
        mult = int(multiplier_str)
        return mult > 0
    except ValueError:
        return False


def validate_period(period: str) -> bool:

    valid_periods = ['day', 'week', 'month', 'quarter', 'year']
    return period in valid_periods


def validate_chart_type(chart_type: str) -> bool:

    valid_types = ['candle', 'line']
    return chart_type in valid_types


def format_price(price: float) -> str:

    return f"${price:,.2f}"


def format_large_number(num: float) -> str:

    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"{num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num/1_000:.2f}K"
    else:
        return f"{num:.2f}"
