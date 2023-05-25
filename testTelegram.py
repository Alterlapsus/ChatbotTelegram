#NOTA 
#EL BOT DE TELEGRAM ES NADA MÁS UNA INTERFAZ LA CUAL ME SERVIRÁ PARA INTERACTUAR CON MI PROGRAMA DE PYTHON

from config import * #importamos el token
import telebot # para manejar la API de Telegram
import time
import threading
# instanciamos el bot de telegram 
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# responde al comando /start
# decoradores
@bot.message_handler(commands=["start","ayuda","help"])
def cmd_start(message):
    # Da la Bienvenida al usuario del bot
    bot.reply_to(message,"Hola ¿Cómo puedo ayudarte?")
    print(message.chat.id)

# responde al comando /boom
# decoradores
@bot.message_handler(commands=["boom","Boom","BOOM"])
def cmd_start(message):
    # Da la Bienvenida al usuario del bot
    bot.reply_to(message,"BIEVENIDOS A MI CHATBOT")
    print(message.chat.id)


# responde a los mensjaes de textos que no son comando 
@bot.message_handler(content_types=["text"])
def bot_mensajes_texto(message):
    #Gestiona los mensjaes de texto recibidos
 
    if message.text.startswith("/"):
        bot.send_message(message.chat.id, "Comando no disponible")
    else:
    #    x = bot.send_message(message.chat.id, "<b>HOLA DE NUEVO!</b>", parse_mode="html", disable_web_page_preview=True)
       time.sleep(3)
       #eliminar mensaje
    #    bot.delete_message(message.chat.id, x.message_id)

        #eliminar mensaje que envía el usuario
    # bot.delete_message(message.chat.id, message.message_id)

       #editar mensaje
    #       bot.edit_message_text("<u>ADIÓS!</u>", message.chat.id,x.message_id, parse_mode="html")

def recibir_mensajes():
    #Es un bucle infinito, comprueba si hay mensajes nuevos
    bot.infinity_polling() 
     
#MAIN 
if __name__ == '__main__':
    # configuramos los comandos disponibles del bot
    bot.set_my_commands([
        telebot.types.BotCommand("/start","Da la bienvenida"),
        telebot.types.BotCommand("/boom","BIENVENIDOS"),
        ])
    print('Iniciando el bot')
    hilo_bot = threading.Thread(name="hilo_bot", target=recibir_mensajes)
    hilo_bot.start()
    print('Fin')

#-----------------------------------------------------------------------


# FORMATO DE MENSAJES HTML
#  texto_html = '<b><u>Formatos HTML</u>:</b>' + '\n' #Negrita y subrayado en HTML(anidación de etiquetas)
#     texto_html+= '<b>NEGRITA</b>' + '\n' #Negrita en HTML
#     texto_html+= '<i>CURSIVA</i>' + '\n' #Cursiva en HTML
#     texto_html+= '<u>SUBRAYADO</u>' + '\n' # Subrayado en HTML
#     texto_html+= '<s>TACHADO</s>' + '\n' # Tachado en HTML
#     texto_html+= '<code>MONOESPACIADO</code>' + '\n' # Monoespaciado en HTML
#     texto_html+= '<span class="tg-spoiler">SPOILER</span>' + '\n' #Spoiler en HTML
#     texto_html+= '<a href="https://github.com/Alterlapsus">ENLACE</a>' + '\n' #Enlace en HTML
#     if message.text.startswith("/"):
#         bot.send_message(message.chat.id, "Comando no disponible")
#     else:
#         bot.send_message(message.chat.id, texto_html, parse_mode="html", disable_web_page_preview=True)