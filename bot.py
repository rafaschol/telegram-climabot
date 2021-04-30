import requests
from credentials import TELEGRAM_TOKEN, OPENWEATHER_TOKEN


API_URL = 'https://api.telegram.org/bot' + TELEGRAM_TOKEN
contador = 0


def enviar_mensaje(chat_id, texto, boton=False):
  global API_URL

  data = {
    'parse_mode': 'Markdown',
    'chat_id': chat_id,
    'text': texto,
  }

  if boton:
    data['reply_markup'] = {
      'keyboard': [ [{'text': 'Consultar el clima'}, {'text': 'Usar el contador'}] ],
      'resize_keyboard': True,
      'one_time_keyboard': True,
    }

  r = requests.post(API_URL + '/sendMessage', json=data)

def info_clima(ciudad):
  response = requests.get('http://api.openweathermap.org/data/2.5/weather?q=' + ciudad + '&units=metric&lang=es&appid=' + OPENWEATHER_TOKEN)
  data = response.json()
  try:
    clima = {
      'descripcion': data['weather'][0]['description'],
      'temperatura': data['main']['temp'],
      'errores': False,
    }
  except:
    clima = {
      'errores': True,
    }
  finally:
    return clima


class MensajeRecibido:
  def __init__(self, id_mensaje, chat_id, texto):
    self.id = id_mensaje
    self.chat_id = chat_id
    self.texto = texto

  def responder(self):
    boton = False

    if self.texto == '/start':
      texto = '¡Bienvenido! Puedes usar los comandos /clima o /contador, o presiona alguno de los botones para ejecutar alguna acción'
      boton = True
    elif self.texto == '/clima' or self.texto == 'Consultar el clima':
      texto = 'Para consultar el clima de un lugar, usa el comando /clima nombreCiudad'
    elif self.texto.startswith('/clima '):
      ciudad = self.texto[7:]
      clima = info_clima(ciudad)
      if not clima['errores']:
        texto = 'En ' + ciudad + ', el clima es "'  + clima['descripcion'] + '", y hay ' + str(clima['temperatura']) + '°C.'
      else:
        texto = 'No pudimos encontrar el lugar que ingresaste...'
    elif self.texto == '/contador' or self.texto == 'Usar el contador':
      global contador
      contador += 1
      texto = '¡Le sumaste 1 al contador! Ahora vale ' + str(contador)
    else:
      texto = 'No se reconoce el comando ingresado... Puedes usar los comandos /clima o /contador, o presionar alguno de los siguientes botones:'
      boton = True
    enviar_mensaje(self.chat_id, texto, boton=boton)
    print('Respondido (#' + str(self.id) + '): "' + str(texto) + '".\n')


class TelegramBot:
  mensajes_sin_responder = []

  def __init__(self, offset=0):
    self.offset = offset

  def actualizar_mensajes(self):
    global API_URL

    response = requests.get(API_URL + '/getUpdates?offset=' + str(self.offset))
    data = response.json()

    for i in data['result']:
      mensaje = MensajeRecibido(id_mensaje=i['update_id'], chat_id=i['message']['chat']['id'], texto=i['message']['text'])
      print('Recibido (#' + str(mensaje.id) + '): "' + str(mensaje.texto) + '".')
      self.offset = mensaje.id + 1 if mensaje.id >= self.offset else self.offset
      self.mensajes_sin_responder.append(mensaje)

  def responder_mensajes(self):
    for mensaje in self.mensajes_sin_responder:
      mensaje.responder()
    self.mensajes_sin_responder = []