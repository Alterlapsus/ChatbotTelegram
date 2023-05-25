from config import *
import telebot
from telebot.types import ReplyKeyboardMarkup, ForceReply, ReplyKeyboardRemove

bot = telebot.TeleBot(TELEGRAM_TOKEN)
usuarios = {}


@bot.message_handler(commands=["start", "help", "ayuda"])
def cmd_start(message):
    markup = ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Bienvenido al restaurante:\nUsa el comando /alta para introducir tus datos y tu pedido", reply_markup=markup)


@bot.message_handler(commands=['alta'])
def cmd_alta(message):
    usuarios[message.chat.id] = {"pedido": {}}
    markup = ForceReply()
    msg = bot.send_message(message.chat.id, "¿Cómo te llamas?", reply_markup=markup)
    bot.register_next_step_handler(msg, preguntar_edad)


def preguntar_edad(message):
    usuarios[message.chat.id]["nombre"] = message.text
    markup = ForceReply()
    msg = bot.send_message(message.chat.id, "¿Cuántos años tienes?", reply_markup=markup)
    bot.register_next_step_handler(msg, preguntar_sexo)


def preguntar_sexo(message):
    if not message.text.isdigit():
        markup = ForceReply()
        msg = bot.send_message(message.chat.id, 'ERROR: Debes indicar un número.\n¿Cuántos años tienes?')
        bot.register_next_step_handler(msg, preguntar_sexo)
    else:
        usuarios[message.chat.id]["edad"] = int(message.text)
        mostrar_menu_pedido(message.chat.id)


def mostrar_menu_pedido(chat_id):
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    menu = {
        "Tortilla de Harina": 10.00,
        "Hamburguesa": 8.00,
        "Churrasco": 12.00,
        "Bebida": 2.00,
        "Finalizar pedido": None
    }
    for articulo, precio in menu.items():
        if precio is not None:
            markup.add(f"{articulo} (${precio})")
        else:
            markup.add(articulo)
    msg = bot.send_message(chat_id, 'Por favor, selecciona un artículo para agregar al pedido:', reply_markup=markup)
    bot.register_next_step_handler(msg, gestionar_pedido)


def gestionar_pedido(message):
    chat_id = message.chat.id
    if message.text == "Finalizar pedido":
        mostrar_resumen_pedido(chat_id)
    else:
        articulo = message.text.split(" $")[0]
        if articulo in usuarios[chat_id]["pedido"]:
            usuarios[chat_id]["pedido"][articulo] += 1
        else:
            usuarios[chat_id]["pedido"][articulo] = 1
        mostrar_menu_pedido(chat_id)


def mostrar_resumen_pedido(chat_id):
    datos_usuario = usuarios[chat_id]
    texto = 'Resumen del pedido:\n\n'
    texto += f'<code> Nombre:</code> {datos_usuario["nombre"]}\n'
    texto += f'<code> Edad..:</code> {datos_usuario["edad"]}\n'
    texto += '<code> Pedido:</code>\n'
    total = 0
    for articulo, cantidad in datos_usuario["pedido"].items():
        precio_unitario = obtener_precio_unitario(articulo)
        precio_total = precio_unitario * cantidad
        texto += f'- {articulo} (${cantidad:.2f}) = ${precio_total:.2f}\n'
        total += precio_total
    texto += f'\n<code> Total:</code> ${total:.2f}\n'
    markup = ReplyKeyboardRemove()
    bot.send_message(chat_id, texto, parse_mode="html", reply_markup=markup)
    print(usuarios)
    del usuarios[chat_id]

# const object1 = {
#   a: 'somestring',
#   b: 42,
#   c: false
# };

# console.log(Object.values(object1));
# // Expected output: Array ["somestring", 42, false]
def mapear_numeros(numeros):
    articulos = []
    for numero in numeros:
        articulo = obtener_precio_unitario(numero)
        articulos.append(articulo)
    return articulos


def obtener_precio_unitario(articulo):
    menu = {
        1: 10.00,
        2: 8.00,
        3: 12.00,
        4: 2.00    
    }
    return menu.get(articulo(object.numeros(menu)))  # 0.00 es el valor predeterminado si el artículo no se encuentra en el menú



# def obtener_precio_unitario(articulo):
#     menu = {
#         "Tortilla de Harina": 10.00,
#         "Hamburguesa": 8.00,
#         "Churrasco": 12.00,
#         "Bebida": 2.00    
#     }
#     return menu.get(articulo, )


if __name__ == '__main__':
    print('Iniciando el bot...')
    bot.infinity_polling()
