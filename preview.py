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
import os
from PIL import Image, ImageDraw, ImageFont

IMG_BASE_URL = os.getenv('IMG_BASE_URL', 'https://thumb.cloud.mail.ru/weblink/thumb/xw20/')
FOLDER = './static/'
FOOTER_TEXT = 'Поздравляем Вас!'
HEADER_TEXT = 'Фото предоставлено D&D Group для ознакомительного просмотра. \n\nБыло сделано {} снимков. \n\nЧтобы приобрести данные фотографии в оригинальном качестве, \nобращайтесь к вашему личному менеджеру. \n\n +7 (925) 066-43-05'


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
            # print('found in ', idx)
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
        # print('\n\n', tree_item)
        try:
            items =  json.dumps(tree_item['list'][0]['items'])
            # print('\n\n {} items: '.format(i), items )
            try:
                index = items.index('.JPG')
                idx_t = i
            except:
                # print('blya')
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
    # print("\n\nFIRST: ", first)
    if (first.split('/')[-1].lower() == 'исходники'):
        url_ = url + quote('Исходники')
        names_ = get_image_names_(url_)
        first_ = names_[0]
        # print("\n\nFIRST 2: ", first_, first_.split('/')[-1].lower())
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

    plt.axis('off')
    figsize = max_width / float(dpi), max_height / float(dpi)
    f = plt.figure(figsize=figsize)
    for i in range(len(imgs)):
        img_it = imgs[i]
        subplot = plt.subplot(num_rows, num_cols, i + 1)
        subplot.axis('off')
        subplot.imshow(img_it)

    name = hashlib.sha1(url.encode('utf-8')).hexdigest()

    file_path = FOLDER + str(name) + '.png'

    f.savefig(file_path)

    return file_path

def create_blank_image(width, height):
  # height = 1340
  # width = 3650
  blank_image = np.zeros((height,width,3), np.uint8)
  blank_image[:, :, :] = (255, 255, 255)
  return blank_image

def put_text2img(text, image, offset, font_size, align='center', fill='black'):
  im = Image.fromarray(image)
  draw = ImageDraw.Draw(im)
  # # здесь узнаем размеры сгенерированного блока текста
  font = ImageFont.truetype("cocon-regular.otf", font_size, encoding='UTF-8')
  draw = ImageDraw.Draw(im).multiline_text(offset, text, fill=fill, font=font)

  result = np.asarray(im)
  return result

def convert_pdf_to_cv2(pdf_path):
    print('reading pdf.png')
    raw_pdf = cv2.imread(pdf_path, cv2.IMREAD_COLOR)
    print('converting pdf.png')
    raw_pdf = cv2.cvtColor(raw_pdf, cv2.COLOR_BGR2RGB)
    print('deleting pdf.png')
    os.remove(pdf_path)
    return raw_pdf

def insert_img2img(front, back, offset):
    x_offset, y_offset = offset
    back[y_offset:y_offset+front.shape[0], x_offset:x_offset+front.shape[1]] = front
    return back

def add_footer_and_header(raw_pdf, file_path, photos_num):
    height = 1600
    width = int(3650 * 2)
    print("Читаю лого")
    watermark = cv2.imread("watermark.jpeg", cv2.IMREAD_COLOR)
    watermark = cv2.cvtColor(watermark, cv2.COLOR_BGR2RGB)
    resized_watermark = cv2.resize(watermark, (0,0), fx=2, fy=2) 
    #HEADER
    print("Создаю хэдер")
    header_blank = create_blank_image(width, height)
    watermark_offset = (100, int((header_blank.shape[0] - resized_watermark.shape[0]) / 2))
    header_logo = insert_img2img(resized_watermark, header_blank, watermark_offset)
    header = put_text2img(HEADER_TEXT.format(photos_num), header_blank, ((width / 2 - 300), ( height / 2 - 350)),  100)
    offset_header = (( int((raw_pdf.shape[1] - header.shape[1])/2), 400))
    new_pdf = insert_img2img(header, raw_pdf, offset_header)
    print("Создаю футер")
    #FOOTER
    footer_blank = create_blank_image(width, height)
    footer = put_text2img(FOOTER_TEXT, footer_blank, (width / 2 - 550, height/ 2 - 30), 130)
    offset = (int((new_pdf.shape[1] - footer.shape[1])/2), new_pdf.shape[0] - footer.shape[0])
    final_pdf = insert_img2img(footer, new_pdf, offset)

    
    final_pil = Image.fromarray(final_pdf)

    new_path = file_path.replace('.png','.pdf')
    final_pil.save(new_path)
    return new_path


def create(url):
    if(url[-1] != '/'):
        url+='/'
    names = get_image_names(url)
    imgs = get_images_by_names(names)
    pdf_name = imgs2pdf(imgs, url)
    nparr = convert_pdf_to_cv2(pdf_name)
    path = add_footer_and_header(nparr,pdf_name, len(imgs) )
    return path

# names = get_image_names('https://cloud.mail.ru/public/5H3P/5ta4qc4fu/')
# imgs = get_images_by_names(names)
# pdf_name = imgs2pdf(imgs, 'https://cloud.mail.ru/public/5H3P/5ta4qc4fu/')
# print(pdf_name)