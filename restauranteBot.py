from config import * # Importar configuraciones
import telebot # Importar el módulo telebot para trabajar con el bot de Telegram
from telebot.types import ForceReply # Importar tipos necesarios del módulo telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests  # Importar el módulo requests para realizar solicitudes HTTP

bot = telebot.TeleBot(TELEGRAM_TOKEN) # Crear una instancia del bot de Telegram

    
usuarios = {} # Diccionario para almacenar los datos de los usuarios
nombres_ingresados = [] # Lista para almacenar los nombres ingresados


menu = {
    "Tortilla de Harina": { # Lista para almacenar los nombres ingresados
        "Grande": 35,
        "Mediana": 25,
        "Pequeña": 12
    },
    "Hamburguesa": { # Menú con opciones de hamburguesa
        "Normal": 15,
        "Doble": 25
    },
    "Churrasco": { # Menú con opciones de churrasco
        "Con papas": 30,
        "Sin papas": 25
    },
    "Bebida": {  # Menú con opciones de bebida
        "Coca-Cola": 8,
        "Sprite": 8,
        "Fanta": 8
    },
    "Finalizar pedido": None # Opción para finalizar el pedido
}

# Diccionario con las imágenes asociadas a cada artículo
card_images = {
    
    "Logo restaurante": "logo_restaurante.jpg",
    "Tortilla de Harina": "tortillaHarina.jpg",
    "Hamburguesa": "hamburguesa.jpg",
    "Churrasco": "churrasco.jpg",
    "Bebida": "bebida.jpg",
    "Menu":"menu.png"
}

@bot.message_handler(commands=["start", "help", "ayuda"])
def cmd_start(message):
    markup = InlineKeyboardMarkup(row_width=2) # Crear un objeto InlineKeyboardMarkup para mostrar botones en línea
    markup.add(InlineKeyboardButton("Agregar nombre", callback_data="agregar_nombre")) # Agregar botón "Agregar nombre"
    markup.add(InlineKeyboardButton("Agregar dirección", callback_data="agregar_direccion"))  # Agregar botón "Agregar dirección"
    bot.send_photo(message.chat.id, open(card_images.get("Logo restaurante", "default.jpg"), "rb")) # Enviar foto del logo del restaurante
    bot.send_message(message.chat.id, "Bienvenido al BOT restaurante KALUSHA:\n Usa los botones para agregar tu nombre y dirección.", 
                     reply_markup=markup) # Enviar mensaje de bienvenida con botones


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    data = call.data
    if data == "agregar_nombre":
        agregar_nombre(chat_id) # Llamar a la función agregar_nombre
    elif data == "agregar_direccion":
        agregar_direccion(chat_id)  # Llamar a la función agregar_direccion
    elif data == "Finalizar pedido":
        solicitar_metodo_pago(chat_id)  # Solicitar el método de pago al finalizar el pedido
    elif data.startswith("metodo_pago:"):
        metodo_pago = data.split(":")[1]
        # Obtener nombre y dirección del usuario  
        nombre = usuarios[chat_id]["nombre"]
        direccion = usuarios[chat_id]["direccion"]
        mostrar_resumen_pedido(chat_id, message_id, nombre, direccion, metodo_pago)  # Cambio de "edad" a "dirección"
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
            bot.send_message(chat_id, f"Has agregado {articulo} {opcion} al pedido.")
            mostrar_menu_pedido(chat_id, usuarios[chat_id].get("nombre"), usuarios[chat_id].get("direccion"))  # Cambio de "edad" a "dirección"

# Funciones para agregar nombre y dirección

def agregar_nombre(chat_id):
    markup = ForceReply()  # Crear un objeto ForceReply para solicitar una respuesta del usuario
    msg = bot.send_message(chat_id, "¿Cómo te llamas?", reply_markup=markup) # Enviar mensaje solicitando el nombre
    bot.register_next_step_handler(msg, guardar_nombre, chat_id)  # Pasamos 'chat_id' como argumento adicional,  # Registrar el siguiente paso de la conversación para guardar el nombre


def agregar_direccion(chat_id):  
    markup = ForceReply()
    msg = bot.send_message(chat_id, "¿Cuál es tu dirección?", reply_markup=markup)  
    bot.register_next_step_handler(msg, guardar_direccion, chat_id)  # Pasamos 'chat_id' como argumento adicional


def guardar_nombre(message, chat_id):
    nombre = message.text  # Obtener el nombre del mensaje del usuario
    if chat_id not in usuarios:
        usuarios[chat_id] = {} # Crear un diccionario para almacenar los datos del usuario si no existe
    usuarios[chat_id]["nombre"] = nombre # Guardar el nombre en el diccionario de datos del usuario
    nombres_ingresados.append(chat_id) # Agregar el chat_id a la lista de nombres ingresados
    agregar_direccion(chat_id)  ## Llamar a la función agregar_direccion para solicitar la dirección


def guardar_direccion(message, chat_id):  # Cambio de "edad" a "dirección"
    direccion = message.text
    if chat_id not in usuarios:
        usuarios[chat_id] = {}
    usuarios[chat_id]["direccion"] = direccion
    mostrar_menu_pedido(chat_id, usuarios[chat_id]["nombre"], usuarios[chat_id]["direccion"])  # Cambio de "edad" a "dirección"


# Funciones para mostrar el menú y submenú del pedido

def mostrar_menu_pedido(chat_id, nombre, direccion):  # Agregamos 'nombre' y 'direccion' como argumentos
    markup = InlineKeyboardMarkup(row_width=2) # Crear un objeto InlineKeyboardMarkup para el markup del mensaje
    buttons = []  # Lista para almacenar los botones de cada fila

    for articulo, opciones in menu.items():
        if opciones is None:
            buttons.append(InlineKeyboardButton(articulo, callback_data=articulo)) # Agregar botón sin opciones
        else:
            buttons.append(InlineKeyboardButton(articulo, callback_data=articulo)) # Agregar botón sin opciones

        # Si la lista de botones alcanza el tamaño de 2, agregamos los botones a la marca de teclado y reiniciamos la lista
        if len(buttons) == 2:
            markup.row(*buttons)  # Agregar los botones de la fila actual a la marca de teclado
            buttons = []  # Reiniciar la lista para la siguiente fila

    # Agregar los botones restantes si hay algún botón sin emparejar
    if buttons:
        markup.row(*buttons) # Agregar los botones de la fila actual a la marca de teclado

    # Si el número total de botones es impar, agregar un botón "Finalizar pedido" que abarque todo el espacio
    if len(menu) % 1 != 0:
        markup.add(InlineKeyboardButton("Finalizar pedido", callback_data="Finalizar pedido"))

# Enviar mensaje con el menú y markup

    bot.send_photo(
    chat_id,
    open(card_images.get("Menu", "default.jpg"), "rb"),
    caption="BIENVENIDO {}! ESTE ES EL MENÚ DE HOY".format(nombre),
    reply_markup=markup
)


def mostrar_submenu_pedido(chat_id, articulo):
    opciones = menu.get(articulo, {}) # Obtener las opciones del artículo del menú
    if opciones:
        markup = InlineKeyboardMarkup(row_width=2) # Obtener las opciones del artículo del menú
        for opcion, precio in opciones.items():
            markup.add(InlineKeyboardButton(f"{opcion} (Q{precio})", callback_data=f"{articulo}:{opcion}"))# Agregar botones para cada opción del submenú
        bot.send_photo(
            chat_id,
            open(card_images.get(articulo, "default.jpg"), "rb"), # Enviar mensaje con el submenú y markup
            caption=f"Elige una opción para {articulo}:",
            reply_markup=markup
        )

# Funciones para obtener el precio unitario y capturar el método de pago

def obtener_precio_unitario(articulo, opcion=None):
    if opcion:
        return menu[articulo][opcion]  # Obtener el precio de la opción específica
    else:
        return menu[articulo] # Obtener el diccionario de opciones del artículo


# Función para capturar el método de pago
def solicitar_metodo_pago(chat_id):
    markup = InlineKeyboardMarkup(row_width=2)# Crear un objeto InlineKeyboardMarkup para el markup del mensaje
    markup.add(InlineKeyboardButton("Efectivo", callback_data="metodo_pago:efectivo"))# Agregar botón para pago en efectivo
    markup.add(InlineKeyboardButton("Tarjeta", callback_data="metodo_pago:tarjeta"))# Agregar botón para pago con tarjeta
    bot.send_message(chat_id, "Selecciona el método de pago:", reply_markup=markup) # Enviar mensaje solicitando el método de pago

# Funcion para guardar mi método de pago

def guardar_metodo_pago(message, chat_id, message_id):
    metodo_pago = message.text
    usuarios[chat_id]["metodo_pago"] = metodo_pago
    mostrar_resumen_pedido(chat_id, message_id, usuarios[chat_id]["nombre"], usuarios[chat_id]["direccion"],
                           metodo_pago)  

# función para enviar el resumen del pedido a otro canal

def enviar_resumen_pedido_nuevo_canal(texto):
    url = f"https://api.telegram.org/bot5885278471:AAFrUUZ15FE0vox8ChgQhYFOaP3CBYQnwwE/sendMessage" #token de mi restaurnteBot
    payload = {
        "chat_id": -1001914796946, #id de mi nuevo canal
        "text": texto, #enviar el mensaje de tipo texto y pasarlo a html
        "parse_mode": "html"
    }
    # hacemos uso de la librería response para enviar un post a través de la URL de la función enviar_resumen_pedido_nuevo_canal
    response = requests.post(url, json=payload)
    if response.status_code != 200: #si no fue exitoso el envió marcar error
        print(f"Error al enviar el mensaje al nuevo canal. Código de estado: {response.status_code}") #imprimir en pantalla error

# función que me permite visualizar un detalle de lo que he comprado usando el chatbot 

def mostrar_resumen_pedido(chat_id, message_id, nombre, direccion, metodo_pago):  # Cambio de "edad" a "direccion"
    datos_usuario = usuarios.get(chat_id, {})

    if datos_usuario:
        texto = '-----------   Resumen del pedido   -----------\n\n'
        texto += f'<code>Nombre:</code> {nombre}\n'
        texto += f'<code>Dirección:</code> {direccion}\n'  # Cambio de "edad" a "direccion"
        texto += '<code>Pedido:</code>\n\n'
        total = 0
        for articulo, opciones in datos_usuario.get("pedido", {}).items():
            texto += f'- {articulo}:\n'
            for opcion, cantidad in opciones.items():
                precio_unitario = obtener_precio_unitario(articulo, opcion)
                subtotal = precio_unitario * cantidad
                texto += f'  {opcion} (Q{precio_unitario}): (Cantidad: {cantidad}) - Subtotal: Q{subtotal}\n'
                total += subtotal
        texto += f'\n<code>Total:</code> Q{int(total)}\n'
        texto += f'<code>Método de Pago:</code> {metodo_pago}\n\n'  # Incluir el método de pago en el texto
        texto += f'\n<code>Tu pedido ha sido solicitado: {nombre}</code>\n'
        bot.send_message(chat_id, texto, reply_to_message_id=message_id, parse_mode="html")
        enviar_resumen_pedido_nuevo_canal(texto)  # Llama a la función y pasa 'texto'

def obtener_articulo_opcion(data):
    parts = data.split(":")
    articulo = parts[0]
    opcion = parts[1] if len(parts) > 1 else None
    return articulo, opcion


if __name__ == '__main__':
    print('Iniciando el bot...')
    bot.infinity_polling()
