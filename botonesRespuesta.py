from config import *
import telebot  # para manejar la API de Telegram
from telebot.types import ReplyKeyboardMarkup  # para crear botones
from telebot.types import ForceReply #para citar un mensaje
from telebot.types import ReplyKeyboardRemove #eliminar botonera

# instanciamos el bot de telegram
bot = telebot.TeleBot(TELEGRAM_TOKEN)
usuarios = {}


# responde a los comandos /start, /help, /ayuda
@bot.message_handler(commands=["start", "help", "ayuda"])
def cmd_start(message):
    # muesta los comandos disponibles
    markup = ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Bienvenido al restaurante:\nUsa el comando /alta para introducir tus datos y tu pedido", reply_markup=markup)
    

#responde al comando /alta 
@bot.message_handler(commands=['alta'])
def cmd_alta(message):
    #preguntar el nombre del usuario
    markup = ForceReply()
    msg = bot.send_message(message.chat.id, "¿Cómo te llamas?", reply_markup=markup)
    bot.register_next_step_handler(msg, preguntar_edad)
 
def preguntar_edad(message):
    usuarios[message.chat.id] = {}
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
        markup = ReplyKeyboardMarkup(one_time_keyboard=True, 
                                     input_field_placeholder="Pulsa un botón",
                                     resize_keyboard=True
                                    )
        markup.add("Hombre", "Mujer")
        msg = bot.send_message(message.chat.id, '¿Cuál es tu sexo?', reply_markup=markup)
        bot.register_next_step_handler(msg, guardar_datos_usuario)

def guardar_datos_usuario(message):
    if message.text != "Hombre" and message.text != "Mujer":
        msg = bot.send_message(message.chat.id, 'ERROR: Sexo no válido.\nPulsa un botón')
        bot.register_next_step_handler(msg,guardar_datos_usuario)
    else: 
        usuarios[message.chat.id]["sexo"] = message.text
        texto = 'Datos ingresados:\n\n' 
        texto+= f'<code> Nombre:</code> {usuarios[message.chat.id]["nombre"]}\n' 
        texto+= f'<code> Edad..:</code> {usuarios[message.chat.id]["edad"]}\n' 
        texto+= f'<code> Sexo..:</code> {usuarios[message.chat.id]["sexo"]}\n' 
        # texto = 'Datos de pedido:\n\n' 
        # texto+= f'<code> Tortilla De Harina:</code> {usuarios[message.chat.id]["tortilla"]}\n' 
        # texto+= f'<code> Hamburguesa:</code> {usuarios[message.chat.id]["hamburguesa"]}\n' 
        # texto+= f'<code> Churrasco:</code> {usuarios[message.chat.id]["churrasco"]}\n' 
        # texto+= f'<code> Bebida..:</code> {usuarios[message.chat.id]["bebida"]}\n'  
        markup = ReplyKeyboardRemove()
        bot.send_message(message.chat.id, texto, parse_mode="html", reply_markup=markup)
        print(usuarios)
        # boorar datos en memoria
        del usuarios[message.chat.id]
        

    # MAIN
if __name__ == '__main__':
    print('Iniciando el bot...')
    #Es un bucle infinito, comprueba si hay mensajes nuevos
    bot.infinity_polling() 







# --------------------------------------------------------
# no funciono código

# responde al comando /alta
# @bot.message_handler(commands=['alta'])
# def cmd_alta(message):
#     # pregunta el nombre del usuario
#     markup = ForceReply()
#     msg = bot.send_message(message.chat.id, '¿Cómo te llamas?', reply_markup=markup)
#     bot.register_next_step_handler(msg, preguntar_edad)

# #realizo un función
#     def preguntar_edad(message):
#         #preguntar la edad del usuario
#         nombre = message.text
#         markup = ForceReply()
#         msg = bot.send_message(message.chat.id, '¿Cúantos años tienes?', reply_markup=(markup))
#         bot.register_next_step_handler(msg, preguntar_sexo)
       

#     def preguntar_sexo(message):
#         #preguntar el sexo del usuario
#         #isdigit es un método que nos devuelve true si el contenido del string es un numero, caso contrario nos devuelve false
#         if not message.text.isdigit(): 
#             #informamos del error y volvemos a preguntar si no es un número
#             markup = ForceReply() 
#             msg = bot.send_message(message.chat.id, 'ERROR: Debes indicar un número.\n ¿Cúantos años tienes?')
#             bot.register_next_step_handler(msg, preguntar_sexo)
#         else: #si se introdujo la edad correctamente 
#             #definimos dos botones 
#             markup = ReplyKeyboardMarkup(one_time_keyboard=True, input_field_placeholder="Pulsa un botón")
#             markup.add("Hombre", "Mujer")
#             #preguntamos por el sexo
#             msg = bot.send_message(message.chat.id, '¿Cúal es tu sexo?', reply_markup=(markup))