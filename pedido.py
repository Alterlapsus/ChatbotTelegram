from config import *
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = telebot.TeleBot(TELEGRAM_TOKEN)
usuarios = {}

menu = {
    "Tortilla de Harina": 10,
    "Hamburguesa": 8,
    "Churrasco": 12,
    "Bebida": 2,
    "Finalizar pedido": None
}

@bot.message_handler(commands=["start", "help", "ayuda"])
def cmd_start(message):
    mostrar_menu_pedido(message.chat.id)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    if call.data == "Finalizar pedido":
        mostrar_resumen_pedido(chat_id, message_id)
    else:
        articulo = call.data
        if chat_id not in usuarios:
            usuarios[chat_id] = {"nombre": "", "edad": 0, "pedido": {}}
        if articulo in usuarios[chat_id]["pedido"]:
            usuarios[chat_id]["pedido"][articulo] += 1
        else:
            usuarios[chat_id]["pedido"][articulo] = 1
        bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)
        bot.send_message(chat_id, f"Has agregado {articulo} al pedido.")
        mostrar_menu_pedido(chat_id)

def mostrar_menu_pedido(chat_id):
    markup = InlineKeyboardMarkup(row_width=2)
    for articulo, precio in menu.items():
        if precio is not None:
            markup.add(InlineKeyboardButton(f"{articulo} (Q{precio})", callback_data=articulo))
        else:
            markup.add(InlineKeyboardButton(articulo, callback_data=articulo))
    bot.send_photo(
        chat_id,
        open("menu_card.jpg", "rb"),
        reply_markup=markup
    )

# def mostrar_detalle_pedido(chat_id):
#     datos_usuario = usuarios[chat_id]
#     texto = 'Detalle del pedido:\n\n'
#     texto += f'Nombre: {datos_usuario["nombre"]}\n'
#     texto += f'Edad: {datos_usuario["edad"]}\n'
#     texto += 'Pedido:\n'
#     for articulo, cantidad in datos_usuario["pedido"].items():
#         texto += f'- {articulo}: {cantidad}\n'
#     bot.send_message(chat_id, texto)

def mostrar_resumen_pedido(chat_id, message_id):
    datos_usuario = usuarios[chat_id]
    texto = 'Resumen del pedido:\n\n'
    texto += f'<code> Nombre:</code> {datos_usuario["nombre"]}\n'
    texto += f'<code> Edad..:</code> {datos_usuario["edad"]}\n'
    texto += '<code> Pedido:</code>\n'
    total = 0
    for articulo, cantidad in datos_usuario["pedido"].items():
        texto += f'- {articulo} (Cantidad: {cantidad})\n'
        total += obtener_precio_unitario(articulo) * cantidad
    texto += f'\n<code> Total:</code> Q{int(total)}\n'
    bot.send_message(chat_id, texto, parse_mode="html")
    # mostrar_detalle_pedido(chat_id)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    if call.data == "Finalizar pedido":
        mostrar_resumen_pedido(chat_id, message_id)
        usuarios.pop(chat_id)  # Eliminar los datos del usuario después de finalizar el pedido
    else:
        articulo = call.data
        if articulo in usuarios[chat_id]["pedido"]:
            usuarios[chat_id]["pedido"][articulo] += obtener_precio_unitario(articulo)
        else:
            usuarios[chat_id]["pedido"][articulo] = obtener_precio_unitario(articulo)
        bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)
        bot.send_message(chat_id, f"Has agregado {articulo} al pedido.")


def obtener_precio_unitario(articulo):
    return menu.get(articulo, 0.00)  # 0.00 es el valor predeterminado si el artículo no se encuentra en el menú

if __name__ == '__main__':
    print('Iniciando el bot...')
    bot.infinity_polling()
