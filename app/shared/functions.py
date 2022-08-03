def message_welcome():
    line_break = "\n"
    message = "Bienvenidos a <b>BotDanielMCondor</b>, podrás descargar música y videos" + line_break
    message += "<u>Comandos disponibles:</u>" + line_break
    message += "    - /help o /start: muestra los comandos disponibles del bot." + line_break
    message += "    - /menu: muestra las opciones menú para descargar musica o videos." + line_break
    return message

def remove_special_char(string: str):
    import re
    regex = "[^A-Za-z0-9-.\u00C0-\u017F]+"
    new_string = re.sub(regex, "", string)
    return new_string.strip()