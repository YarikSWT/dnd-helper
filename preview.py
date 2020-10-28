from bs4 import BeautifulSoup as soup
import requests
from urllib.request import urlopen as uReq
from urllib.parse import quote   
import json
import numpy as np
import urllib
import cv2
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.image as image
import math
from datetime import datetime
import hashlib
matplotlib.use('Agg')


IMG_BASE_URL = 'https://thumb.cloud.mail.ru/weblink/thumb/xw20/'
FOLDER = './static/'



def get_image_names(url):
    formedUrl = url.replace('/Исходники', '')
    if(formedUrl[-1] != '/'):
        formedUrl+='/'
    page_url = formedUrl + quote('Исходники')

    uClient = uReq(page_url)

    page_soup = soup(uClient.read(), "html.parser")
    uClient.close()

    found = page_soup.findAll('script')

    script = found[29]
    text = str(script)
    text = text.replace('window.cloudSettings =', '')
    text = text.replace('<script>', '')
    text = text.replace('</script>', '')
    text = text.replace('</script>', '')
    text = text.replace(';', '')
    text = text.replace('\\x', '')
    text = text.replace('\\x', '')

    print('start parse to json')

    jsn = json.loads(text)

    imgs_names = jsn['folders']['tree'][1]['list'][0]['items']

    print('imgs_names: ', imgs_names)

    # print(imgs_names)

    return imgs_names

def url_to_image(url):
  # download the image, convert it to a NumPy array, and then read
	# it into OpenCV format
  print('trying to load image from url ', url)
  resp = urllib.request.urlopen(url)
  print('done load')
  image = np.asarray(bytearray(resp.read()), dtype="uint8")
  image_cvt = cv2.imdecode(image, cv2.IMREAD_COLOR)
  image = cv2.cvtColor(image_cvt, cv2.COLOR_BGR2RGB)
  return image

def get_images_by_names(names):

    normalized_names = []
    for name in names:
        splited = name.split('Исходники')
        norma = splited[0] + quote('Исходники') + splited[1]
        normalized_names.append(norma)

    print('normalized: ', len(normalized_names))

    imgs = [url_to_image(IMG_BASE_URL + img_name) for img_name in normalized_names]

    print('Downloaded {} images'.format(len(imgs)))

    return imgs


def imgs2pdf(imgs, url):

    imgs_num = len(imgs)

    num_cols = 6
    num_rows = math.ceil( imgs_num / num_cols )

    max_height = num_rows * 170
    max_width = num_cols * 170
    dpi = 10

    watermark = cv2.imread("watermark.jpeg", cv2.IMREAD_COLOR)

    plt.axis('off')
    figsize = max_width / float(dpi), max_height / float(dpi)
    f = plt.figure(figsize=figsize)
    f.suptitle('Фото предоставленно DnD Group для ознакомительного просмотра. \n Чтобы приобрести данные фотографии в оригинальном качестве, обращайтесь к менеджеру.', fontsize=50)
    for i in range(len(imgs)):
        img_it = imgs[i]
        subplot = plt.subplot(num_rows, num_cols, i + 1)
        subplot.axis('off')
        subplot.imshow(img_it)
    f.figimage(watermark, max_width/2, max_height/2, zorder=3, alpha=.5)
    now = datetime.now()

    name = hashlib.sha1(url.encode('utf-8')).hexdigest()

    file_path = FOLDER + str(name) + '.pdf'

    f.savefig(file_path)

    return file_path


def create(url):
    names = get_image_names(url)
    imgs = get_images_by_names(names)
    pdf_name = imgs2pdf(imgs, url)
    return pdf_name


# names = get_image_names('https://cloud.mail.ru/public/5H3P/5ta4qc4fu/')
# imgs = get_images_by_names(names)
# pdf_name = imgs2pdf(imgs, 'https://cloud.mail.ru/public/5H3P/5ta4qc4fu/')
# print(pdf_name)