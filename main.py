"""
Bot de Telegram para análisis de acciones estadounidenses
Obtiene precios históricos y calcula medias móviles (SMA 200/50)
"""

import os
from telebot.async_telebot import AsyncTeleBot
from telebot import types
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.asyncio_storage import StateMemoryStorage
import asyncio

# Importar módulos propios
from config import bot_token
import keyboard
import utils
from historical_prices import get_historical_prices_chart
from sma import get_sma_analysis
from full_data import get_full_data

# Crear instancia del bot con almacenamiento de estados
state_storage = StateMemoryStorage()
bot = AsyncTeleBot(bot_token, state_storage=state_storage)



# Definir estados para el flujo de conversación
class HistoricalPricesStates(StatesGroup):
    """Estados para el flujo de Historical Prices"""
    ticker = State()
    start_date = State()
    end_date = State()
    multiplier = State()
    period = State()
    chart_type = State()


class SMAStates(StatesGroup):
    """Estados para el flujo de SMA Analysis"""
    ticker = State()


class FullDataStates(StatesGroup):
    """Estados para el flujo de Full Data"""
    ticker = State()


# ============================================
# COMANDOS PRINCIPALES
# ============================================

@bot.message_handler(commands=['start'])
async def start_command(message):
    """Comando /start - Inicia el bot y muestra el menú principal"""
    await bot.send_message(
        message.chat.id,
        utils.WELCOME_MESSAGE,
        reply_markup=keyboard.main_menu(),
        parse_mode='Markdown'
    )


@bot.message_handler(commands=['Guide'])
async def guide_command(message):
    """Comando /Guide - Muestra la guía de uso"""
    await bot.send_message(
        message.chat.id,
        utils.GUIDE_MESSAGE,
        parse_mode='Markdown'
    )


@bot.message_handler(commands=['Historical_prices'])
async def historical_prices_command(message):
    """Comando /Historical_prices - Inicia el flujo de precios históricos"""
    await start_historical_prices(message)


@bot.message_handler(commands=['SMA'])
async def sma_command(message):
    """Comando /SMA - Inicia el flujo de análisis SMA"""
    await start_sma_analysis(message)


# ============================================
# MANEJO DE BOTONES DEL MENÚ PRINCIPAL
# ============================================

@bot.message_handler(func=lambda message: message.text == "📈 Historical Prices")
async def historical_prices_button(message):
    """Botón de Historical Prices"""
    await start_historical_prices(message)


@bot.message_handler(func=lambda message: message.text == "📊 SMA Analysis")
async def sma_button(message):
    """Botón de SMA Analysis"""
    print(f"🔵 DEBUG: SMA button pressed by user {message.from_user.id}")
    await start_sma_analysis(message)


@bot.message_handler(func=lambda message: message.text == "📋 Full Data")
async def full_data_button(message):
    """Botón de Full Data"""
    await start_full_data(message)


@bot.message_handler(func=lambda message: message.text == "ℹ️ Guide")
async def guide_button(message):
    """Botón de Guide"""
    await guide_command(message)


@bot.message_handler(func=lambda message: message.text in ["🔙 Back to Menu", "❌ Cancel"])
async def back_to_menu(message):
    """Botón para volver al menú principal"""
    await bot.delete_state(message.from_user.id, message.chat.id)
    await bot.send_message(
        message.chat.id,
        "Regresando al menú principal...",
        reply_markup=keyboard.main_menu()
    )


# ============================================
# FLUJO DE HISTORICAL PRICES
# ============================================

async def start_historical_prices(message):
    """Inicia el flujo de Historical Prices"""
    await bot.set_state(message.from_user.id, HistoricalPricesStates.ticker, message.chat.id)
    await bot.send_message(
        message.chat.id,
        utils.PROMPT_TICKER,
        reply_markup=keyboard.cancel_keyboard()
    )


async def process_ticker_historical(message):
    """Procesa el ticker ingresado"""
    ticker = message.text.strip()
    
    # Validar ticker
    if not utils.validate_ticker(ticker):
        await bot.send_message(message.chat.id, utils.ERROR_INVALID_TICKER)
        return
    
    # Guardar ticker en el estado
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['ticker'] = ticker
    
    # Pasar al siguiente estado
    await bot.set_state(message.from_user.id, HistoricalPricesStates.start_date, message.chat.id)
    await bot.send_message(message.chat.id, utils.PROMPT_START_DATE)


async def process_start_date(message):
    """Procesa la fecha inicial"""
    start_date = message.text.strip()
    
    # Validar fecha
    if not utils.validate_date(start_date):
        await bot.send_message(message.chat.id, utils.ERROR_INVALID_DATE)
        return
    
    # Guardar fecha en el estado
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['start_date'] = start_date
    
    # Pasar al siguiente estado
    await bot.set_state(message.from_user.id, HistoricalPricesStates.end_date, message.chat.id)
    await bot.send_message(message.chat.id, utils.PROMPT_END_DATE)


async def process_end_date(message):
    """Procesa la fecha final"""
    end_date = message.text.strip()
    
    # Validar fecha
    if not utils.validate_date(end_date):
        await bot.send_message(message.chat.id, utils.ERROR_INVALID_DATE)
        return
    
    # Guardar fecha en el estado
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['end_date'] = end_date
    
    # Pasar al siguiente estado
    await bot.set_state(message.from_user.id, HistoricalPricesStates.multiplier, message.chat.id)
    await bot.send_message(message.chat.id, utils.PROMPT_MULTIPLIER)


async def process_multiplier(message):
    """Procesa el multiplicador"""
    multiplier_str = message.text.strip()
    
    # Validar multiplicador
    if not utils.validate_multiplier(multiplier_str):
        await bot.send_message(message.chat.id, utils.ERROR_INVALID_MULTIPLIER)
        return
    
    # Guardar multiplicador en el estado
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['multiplier'] = int(multiplier_str)
    
    # Pasar al siguiente estado
    await bot.set_state(message.from_user.id, HistoricalPricesStates.period, message.chat.id)
    await bot.send_message(
        message.chat.id,
        utils.PROMPT_PERIOD,
        reply_markup=keyboard.period_keyboard()
    )


async def process_period(message):
    """Procesa el periodo"""
    period = message.text.strip()
    
    # Validar periodo
    if not utils.validate_period(period):
        await bot.send_message(message.chat.id, utils.ERROR_INVALID_PERIOD)
        return
    
    # Guardar periodo en el estado
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['period'] = period
    
    # Pasar al siguiente estado
    await bot.set_state(message.from_user.id, HistoricalPricesStates.chart_type, message.chat.id)
    await bot.send_message(
        message.chat.id,
        utils.PROMPT_CHART_TYPE,
        reply_markup=keyboard.chart_type_keyboard()
    )


async def process_chart_type(message):
    """Procesa el tipo de gráfico y genera el resultado"""
    chart_type = message.text.strip()
    
    # Validar tipo de gráfico
    if not utils.validate_chart_type(chart_type):
        await bot.send_message(message.chat.id, utils.ERROR_INVALID_CHART_TYPE)
        return
    
    # Obtener todos los datos del estado
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        ticker = data['ticker']
        start_date = data['start_date']
        end_date = data['end_date']
        multiplier = data['multiplier']
        period = data['period']
    
    # Enviar mensaje de espera
    await bot.send_message(
        message.chat.id,
        utils.SUCCESS_GENERATING_CHART,
        reply_markup=keyboard.main_menu()
    )
    
    # Generar gráfico (ejecutar en bucle de eventos)
    try:
        # Ejecutar función síncrona en el bucle de eventos
        loop = asyncio.get_event_loop()
        chart_path = await loop.run_in_executor(
            None,
            get_historical_prices_chart,
            ticker, multiplier, period, start_date, end_date, chart_type
        )
        
        if chart_path and os.path.exists(chart_path):
            # Enviar gráfico
            with open(chart_path, 'rb') as photo:
                await bot.send_photo(
                    message.chat.id,
                    photo,
                    caption=f"📈 {ticker} - {start_date} to {end_date}"
                )
            
            # Eliminar archivo temporal
            os.remove(chart_path)
            
            await bot.send_message(message.chat.id, utils.SUCCESS_CHART_GENERATED)
        else:
            await bot.send_message(message.chat.id, utils.ERROR_NO_DATA)
    
    except Exception as e:
        await bot.send_message(message.chat.id, f"❌ Error: {str(e)}")
    
    # Limpiar estado
    await bot.delete_state(message.from_user.id, message.chat.id)


# ============================================
# FLUJO DE SMA ANALYSIS
# ============================================

async def start_sma_analysis(message):
    """Inicia el flujo de SMA Analysis"""
    print(f"🟢 DEBUG: Starting SMA analysis for user {message.from_user.id}")
    await bot.set_state(message.from_user.id, SMAStates.ticker, message.chat.id)
    print(f"🟡 DEBUG: State set to SMAStates.ticker")
    await bot.send_message(
        message.chat.id,
        utils.PROMPT_TICKER,
        reply_markup=keyboard.cancel_keyboard()
    )
    print(f"🟠 DEBUG: Prompt sent to user")


async def process_ticker_sma(message):
    """Procesa el ticker para análisis SMA"""
    print(f"🔴 DEBUG: Processing ticker in SMA state. Message: {message.text}")
    ticker = message.text.strip()
    
    # DEBUG: Verificar estado actual
    current_state = await bot.get_state(message.from_user.id, message.chat.id)
    print(f"🟣 DEBUG: Current state: {current_state}")
    
    # Validar ticker
    if not utils.validate_ticker(ticker):
        print(f"❌ DEBUG: Invalid ticker: {ticker}")
        await bot.send_message(message.chat.id, utils.ERROR_INVALID_TICKER)
        return
    
    print(f"✅ DEBUG: Valid ticker: {ticker}")
    # Enviar mensaje de espera
    await bot.send_message(
        message.chat.id,
        utils.SUCCESS_CALCULATING_SMA,
        reply_markup=keyboard.main_menu()
    )
    
    # Calcular SMA
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, get_sma_analysis, ticker)
        
        await bot.send_message(
            message.chat.id,
            result,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        await bot.send_message(message.chat.id, f"❌ Error: {str(e)}")
    
    # Limpiar estado
    await bot.delete_state(message.from_user.id, message.chat.id)


# ============================================
# FLUJO DE FULL DATA
# ============================================

async def start_full_data(message):
    """Inicia el flujo de Full Data"""
    await bot.set_state(message.from_user.id, FullDataStates.ticker, message.chat.id)
    await bot.send_message(
        message.chat.id,
        utils.PROMPT_TICKER,
        reply_markup=keyboard.cancel_keyboard()
    )


async def process_ticker_full_data(message):
    """Procesa el ticker para Full Data"""
    ticker = message.text.strip()
    
    # Validar ticker
    if not utils.validate_ticker(ticker):
        await bot.send_message(message.chat.id, utils.ERROR_INVALID_TICKER)
        return
    
    # Enviar mensaje de espera
    await bot.send_message(
        message.chat.id,
        utils.STATUS_FETCHING_DATA,
        reply_markup=keyboard.main_menu()
    )
    
    # Obtener datos completos
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, get_full_data, ticker)
        
        await bot.send_message(
            message.chat.id,
            result,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        await bot.send_message(message.chat.id, f"❌ Error: {str(e)}")
    
    # Limpiar estado
    await bot.delete_state(message.from_user.id, message.chat.id)


# ============================================
# MANEJO DE MENSAJES NO RECONOCIDOS
# ============================================
# Handler que maneja TODOS los mensajes de texto y verifica estados manualmente
@bot.message_handler(func=lambda message: True, content_types=['text'])
async def handle_text_messages(message):
    """Handler universal que verifica estados y procesa mensajes"""
    # Obtener estado actual
    current_state = await bot.get_state(message.from_user.id, message.chat.id)
    print(f"⚪ DEBUG: Message='{message.text}', State={current_state}")
    
    # Procesar según el estado
    if current_state == "SMAStates:ticker":
        print(f"🔴 DEBUG: Processing SMA ticker")
        await process_ticker_sma(message)
        return
    elif current_state == "HistoricalPricesStates:ticker":
        await process_ticker_historical(message)
        return
    elif current_state == "HistoricalPricesStates:start_date":
        await process_start_date(message)
        return
    elif current_state == "HistoricalPricesStates:end_date":
        await process_end_date(message)
        return
    elif current_state == "HistoricalPricesStates:multiplier":
        await process_multiplier(message)
        return
    elif current_state == "HistoricalPricesStates:period":
        await process_period(message)
        return
    elif current_state == "HistoricalPricesStates:chart_type":
        await process_chart_type(message)
        return
    elif current_state == "FullDataStates:ticker":
        await process_ticker_full_data(message)
        return
    else:
        # No hay estado activo - mensaje no reconocido
        if message.text not in ["📈 Historical Prices", "📊 SMA Analysis", "📋 Full Data", "ℹ️ Guide", "🔙 Back to Menu", "❌ Cancel"]:
            await bot.send_message(
                message.chat.id,
                "❓ Comando no reconocido. Usa /Guide para ver las opciones disponibles.",
                reply_markup=keyboard.main_menu()
            )


# ============================================
# FUNCIÓN PRINCIPAL
# ============================================

async def main():
    """Función principal para ejecutar el bot"""
    print("🤖 Bot de Telegram iniciado...")
    print("✅ Esperando mensajes...")
    
    try:
        await bot.infinity_polling(skip_pending=True)
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Stocks Bot - Iniciando...")
    print("=" * 50)
    
    # Ejecutar el bot
    asyncio.run(main())
