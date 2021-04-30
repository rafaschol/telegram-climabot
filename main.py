import bot

bot = bot.TelegramBot()

while True:
  bot.actualizar_mensajes()
  bot.responder_mensajes()