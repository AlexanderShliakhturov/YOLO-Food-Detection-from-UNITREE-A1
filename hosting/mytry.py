import requests as req
import os
from zipfile import ZipFile

our_url = 'http://127.0.0.1:8000/'
ml_url = 'http://127.0.0.1:8080/vidos'
host_url = 'http://127.0.0.1:пока хз'


# С джанго на мл
files = {'file': open('lab3.py', 'rb')}
out = req.post(ml_url, files=files, stream=True)
#os.remove('lab3.py')
# С мл на джанго ответ с мл пришел в out и мы считаем весь архив в котором 3 файлика соответственно
with open('pack.zip', 'wb') as fd:
    for chunk in out.iter_content(chunk_size=1024*10): #128 изначально
        fd.write(chunk)
# С джанго на хост передадим туда архив там распакуем и начнем мутить грязь с айди
fd = 'pack.zip'  #да да костыль не нравится - предлагай!
with ZipFile(fd, 'r') as f:
        f.extractall('./media') #все три файла лежат в медиа
a = []
for root, dirs, files in os.walk("./media"):  
    for filename in files:
        data = {'file': open(f'{root}/{filename}', 'rb')}
        host = req.post(host_url, files=data, stream=True) #послал на fapi содержит айдишник
        a.append(host)
        os.remove(f'{root}/{filename}')
# сформирован список айдишников они лежат в а
# в этой же вьюшке нужно 3 анкера с ссылками ввиде айди а в них гет запрос на хост
        
# С хоста на джанго распаковка хранение возвращаем айдишники и ебля с загрузой и тд - члень