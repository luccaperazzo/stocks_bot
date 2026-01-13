"""
Teclados personalizados para el bot de Telegram
Define la interfaz de usuario con botones interactivos
"""

from telebot import types


def main_menu():
    """
    Menú principal del bot con opciones disponibles
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    btn1 = types.KeyboardButton("📈 Historical Prices")
    btn2 = types.KeyboardButton("📊 SMA Analysis")
    btn3 = types.KeyboardButton("📋 Full Data")
    btn4 = types.KeyboardButton("ℹ️ Guide")
    
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    
    return markup


def chart_type_keyboard():
    """
    Teclado para seleccionar el tipo de gráfico
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    
    btn1 = types.KeyboardButton("candle")
    btn2 = types.KeyboardButton("line")
    
    markup.add(btn1, btn2)
    
    return markup


def period_keyboard():
    """
    Teclado para seleccionar el periodo de tiempo
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=3)
    
    btn1 = types.KeyboardButton("day")
    btn2 = types.KeyboardButton("week")
    btn3 = types.KeyboardButton("month")
    btn4 = types.KeyboardButton("quarter")
    btn5 = types.KeyboardButton("year")
    
    markup.add(btn1, btn2, btn3)
    markup.add(btn4, btn5)
    
    return markup


def back_to_menu_keyboard():
    """
    Teclado para regresar al menú principal
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    btn = types.KeyboardButton("🔙 Back to Menu")
    markup.add(btn)
    
    return markup


def cancel_keyboard():
    """
    Teclado para cancelar la operación actual
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    btn = types.KeyboardButton("❌ Cancel")
    markup.add(btn)
    
    return markup
