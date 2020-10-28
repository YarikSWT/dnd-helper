from bs4 import BeautifulSoup as soup
import requests
from urllib.request import urlopen as uReq
from urllib.parse import quote   
import json
page_url = 'https://cloud.mail.ru/public/5H3P/5ta4qc4fu/' + quote('Исходники')
IMG_BASE_URL = 'https://thumb.cloud.mail.ru/weblink/thumb/xw20/'

uClient = uReq(page_url)

page_soup = soup(uClient.read(), "html.parser")
uClient.close()

found = page_soup.findAll('script')


script = found[28]
text = str(script)
text = text.replace('window.cloudSettings =', '')
text = text.replace('<script>', '')
text = text.replace('</script>', '')
text = text.replace('</script>', '')
text = text.replace(';', '')
text = text.replace('\\x', '')
text = text.replace('\\x', '')

json = json.loads(text)

imgs_names = json['folders']['tree'][1]['list'][0]['items']

print(imgs_names)
