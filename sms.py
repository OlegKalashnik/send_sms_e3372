from huawei_lte_api.Connection import Connection
from huawei_lte_api.Client import Client

import requests
import xmltodict

import time

# создаём клиента для проверки оператора, как проверить по другому не придумал
class plmnClient:
  def __init__(self, host='192.168.8.1'):
    self.session = requests.Session()
    try:
      r = self.session.get(f'http://{host}/html/home.html', allow_redirects=False, timeout=(0.5, 0.5))
      try:
        r = self.session.get(f'http://{host}/api/net/current-plmn', allow_redirects=False, timeout=(0.5, 0.5))
      except:
        pass
      try:
        self.plmn = xmltodict.parse(r.text)['response']['FullName']
      except:
        self.plmn = False
    except requests.exceptions.ConnectTimeout as e:
      # print (e)
      self.plmn = False
      return

# непосредственно отправка сообщений
def send_message (url, phone_number, message):
  try:
    with Connection(url) as connection:
      client = Client(connection)
      if client.sms.send_sms([phone_number], message) == 'OK':
        print('Модем принял запрос')
        print(f'{url} {phone_number} {message}')
      else:
        print('Error')
    return True
  except:
    print(url, 'Error')
    return False   # если не получится то вернём фолс чтобы больше не мучить этот айпишник

# читаем номера и сообщения
with open('mes.txt', 'r', encoding='utf-8') as f:
  l = f.readlines()

args = list(
  filter(
    lambda x: len(x) == 2,
    map(
      lambda x: x.split(' '),
      filter(
        lambda x: len(x),
        map(
          lambda x: x.strip(),
          l
        )
      )
    )
  )  
)
# если нужно отправлять только с определённого оператора
operator = ''
with open('operator.txt', 'r') as f:
  operator = f.read().strip()
# список айпишников
with open('urls.txt', 'r') as f:
  urls = f.readlines()
# перебираем айпишки и внутри каждого перебираем сообщения
for url in urls:
  if len(url.strip()):
    if len(operator):   # если оператор имеет значение
      plmn = plmnClient(url.strip())
      if plmn.plmn:
        if operator.lower() in plmn.plmn.lower():
          for mes in args:
            send_message(f"http://{url.strip()}/", mes[0], mes[1])
            time.sleep(3)
        else:
          print(f'http://{url.strip()} Оператор{plmn.plmn}')
      else:
        print(f'http://{url.strip()} Не достучались')
    else:   # если оператор не важен
      plmn = plmnClient(url.strip())   # проверяем наличие хоть какого-то оператора чтобы не отправлять с нерабочего модема и не получать ошибку
      if plmn.plmn:
        answer = True
        for mes in args:
          if answer:
            answer = send_message(f"http://{url.strip()}/", mes[0], mes[1])
            time.sleep(3)
      else:
        print(f'http://{url.strip()} Не достучались')
