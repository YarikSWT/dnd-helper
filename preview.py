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
import random
matplotlib.use('Agg')


IMG_BASE_URL = os.getenv('IMG_BASE_URL', 'https://thumb.cloud.mail.ru/weblink/thumb/xw20/')
FOLDER = './static/'



def get_image_names_(url):
    uClient = uReq(url)

    page_soup = soup(uClient.read(), "html.parser")
    uClient.close()

    found = page_soup.findAll('script')

    idx = 23

    for i in range(len(found)):
        script = found[i]
        test = str(script)
        try:
            index = test.index('window.cloudSettings')
            idx = i
            print('found in ', idx)
            break
        except:
            continue

    text = str(script)
    text = text.replace('window.cloudSettings =', '')
    text = text.replace('<script>', '')
    text = text.replace('</script>', '')
    text = text.replace('</script>', '')
    text = text.replace(';', '')
    text = text.replace('\\x', '')
    text = text.replace('\\x', '')

    jsn = json.loads(text)
    tree = jsn['folders']['tree']

    idx_t = 0
    for i in range(len(tree)):
        tree_item = tree[i]
        print('\n\n', tree_item)
        try:
            items =  json.dumps(tree_item['list'][0]['items'])
            # print('\n\n {} items: '.format(i), items )
            try:
                index = items.index('.JPG')
                idx_t = i
            except:
                print('blya')
                try:
                    index = items.index('.JPEG')
                    idx_t = i
                except:
                    continue
        except:
            continue

    imgs_names = tree[idx_t]['list'][0]['items']

    return imgs_names

def get_image_names(url):
    names = get_image_names_(url)
    first = names[0]
    print("\n\nFIRST: ", first)
    if (first.split('/')[-1].lower() == 'исходники'):
        url_ = url + quote('Исходники')
        names_ = get_image_names_(url_)
        first_ = names_[0]
        print("\n\nFIRST 2: ", first_, first_.split('/')[-1].lower())
        if (first_.split('/')[-1].lower() == 'исходники'):
            url__ = url + quote('исходники')
            names__ = get_image_names_(url__)
            return names__
        else:
            return names_
    else:
        return names

def url_to_image(url):
  # download the image, convert it to a NumPy array, and then read
	# it into OpenCV format
#   print('trying to load image from url ', url)
  resp = urllib.request.urlopen(url)
#   print('done load')
  image = np.asarray(bytearray(resp.read()), dtype="uint8")
  image_cvt = cv2.imdecode(image, cv2.IMREAD_COLOR)
  image = cv2.cvtColor(image_cvt, cv2.COLOR_BGR2RGB)
  return image

def get_images_by_names(names):

    imgs = [url_to_image(IMG_BASE_URL + quote(img_name)) for img_name in names]

    print('Downloaded {} images'.format(len(imgs)))

    random.shuffle(imgs)
    print('Images was Shuffled')
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