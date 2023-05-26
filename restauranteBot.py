from config import *
import telebot
from telebot.types import ForceReply
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = telebot.TeleBot(TELEGRAM_TOKEN)
usuarios = {}

menu = {
    "Tortilla de Harina": {
        "Grande": 12,
        "Mediana": 10,
        "Pequeña": 8
    },
    "Hamburguesa": {
        "Normal": 8,
        "Doble": 12
    },
    "Churrasco": {
        "Con papas": 12,
        "Sin papas": 10
    },
    "Bebida": {
        "Coca-Cola": 2,
        "Sprite": 2,
        "Fanta": 2
    },
    "Finalizar pedido": None
}


@bot.message_handler(commands=["start", "help", "ayuda"])
def cmd_start(message):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("Agregar nombre", callback_data="agregar_nombre"))
    markup.add(InlineKeyboardButton("Agregar edad", callback_data="agregar_edad"))
    bot.send_message(message.chat.id, "Bienvenido al restaurante:\nUsa los botones para agregar tu nombre y edad.",
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    data = call.data
    if data == "agregar_nombre":
        agregar_nombre(chat_id)
    elif data == "agregar_edad":
        agregar_edad(chat_id)
    elif data == "Finalizar pedido":
        mostrar_resumen_pedido(chat_id, message_id, usuarios[chat_id]["nombre"], usuarios[chat_id]["edad"])
        usuarios.pop(chat_id)
    elif data in menu:
        mostrar_submenu_pedido(chat_id, data)
    else:
        articulo, opcion = obtener_articulo_opcion(data)
        if articulo in menu and opcion in menu[articulo]:
            if "pedido" not in usuarios[chat_id]:
                usuarios[chat_id]["pedido"] = {}
            if articulo in usuarios[chat_id]["pedido"]:
                usuarios[chat_id]["pedido"][articulo][opcion] += 1
            else:
                usuarios[chat_id]["pedido"][articulo] = {opcion: 1}
            bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)
            bot.send_message(chat_id, f"Has agregado {opcion} de {articulo} al pedido.")
            mostrar_menu_pedido(chat_id, usuarios[chat_id].get("nombre"), usuarios[chat_id].get("edad"))



def agregar_nombre(chat_id):
    markup = ForceReply()
    msg = bot.send_message(chat_id, "¿Cómo te llamas?", reply_markup=markup)
    bot.register_next_step_handler(msg, guardar_nombre, chat_id)  # Pasamos 'chat_id' como argumento adicional


def agregar_edad(chat_id):
    markup = ForceReply()
    msg = bot.send_message(chat_id, "¿Cuántos años tienes?", reply_markup=markup)
    bot.register_next_step_handler(msg, guardar_edad, chat_id)  # Pasamos 'chat_id' como argumento adicional


def guardar_nombre(message, chat_id):
    nombre = message.text
    if chat_id not in usuarios:
        usuarios[chat_id] = {}
    usuarios[chat_id]["nombre"] = nombre
    agregar_edad(chat_id)


def guardar_edad(message, chat_id):
    edad = message.text
    if chat_id not in usuarios:
        usuarios[chat_id] = {}
    usuarios[chat_id]["edad"] = edad
    mostrar_menu_pedido(chat_id, usuarios[chat_id]["nombre"], usuarios[chat_id]["edad"])



def mostrar_menu_pedido(chat_id, nombre, edad):  # Agregamos 'nombre' y 'edad' como argumentos
    markup = InlineKeyboardMarkup(row_width=2)
    for articulo, opciones in menu.items():
        if opciones is None:
            markup.add(InlineKeyboardButton(articulo, callback_data=articulo))
        else:
            markup.add(InlineKeyboardButton(articulo, callback_data=articulo))
    bot.send_photo(
        chat_id,
        open("menu_card.jpg", "rb"),
        reply_markup=markup
    )


def mostrar_submenu_pedido(chat_id, articulo):
    opciones = menu.get(articulo, {})
    if opciones:
        markup = InlineKeyboardMarkup(row_width=2)
        for opcion, precio in opciones.items():
            markup.add(InlineKeyboardButton(f"{opcion} (Q{precio})", callback_data=f"{articulo}:{opcion}"))
        bot.send_photo(
            chat_id,
            open("submenu_image.jpg", "rb"),
            caption=f"Elige una opción para {articulo}:",
            reply_markup=markup
        )


def obtener_precio_unitario(articulo, opcion=None):
    if opcion:
        return menu[articulo][opcion]
    else:
        return menu[articulo]


def mostrar_resumen_pedido(chat_id, message_id, nombre, edad):
    datos_usuario = usuarios.get(chat_id, {})

    if datos_usuario:
        texto = 'Resumen del pedido:\n\n'
        texto += f'<code>Nombre:</code> {nombre}\n'
        texto += f'<code>Edad:</code> {edad}\n\n'
        texto += '<code>Pedido:</code>\n\n'
        total = 0
        for articulo, opciones in datos_usuario.get("pedido", {}).items():
            texto += f'- {articulo}:\n'
            for opcion, cantidad in opciones.items():
                precio_unitario = obtener_precio_unitario(articulo, opcion)
                subtotal = precio_unitario * cantidad
                texto += f'  {opcion} (Cantidad: {cantidad}) - Subtotal: Q{subtotal}\n'
                total += subtotal
        texto += f'\n<code>Total:</code> Q{int(total)}\n'
        texto += f'\n<code>Tu pedido ha sido solicitado:{nombre}</code>\n'
        bot.send_message(chat_id, texto, reply_to_message_id=message_id, parse_mode="html")





def obtener_articulo_opcion(data):
    articulo, opcion = data.split(":")
    return articulo, opcion


if __name__ == '__main__':
    print('Iniciando el bot...')
    bot.infinity_polling()
