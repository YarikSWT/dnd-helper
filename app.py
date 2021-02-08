from flask import Flask, request, render_template, session, flash, redirect, \
    url_for, jsonify
# from celery import Celery
from urllib.parse import unquote
import os
import time
import preview
import random
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
import base64
BLOCK_SIZE = 32 # Bytes

secret_key = b'Sixteen byte key'
cipher = AES.new(secret_key, AES.MODE_ECB)

DOMAIN = os.getenv('DOMAIN', 'http://localhost:5000')
REDIS_URL = os.getenv('REDIS_URL', 'localhost')

app = Flask(__name__, static_url_path = "/static")
app.config['SECRET_KEY'] = 'top-secret!'

# # Celery configuration
# app.config['CELERY_BROKER_URL'] = 'redis://' + REDIS_URL + ':6379/0'
# app.config['CELERY_RESULT_BACKEND'] = 'redis://' + REDIS_URL + ':6379/0'

# # Initialize Celery
# celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
# celery.conf.update(app.config)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/create-preview-old')
def create_preview():
    mail_url = request.args.get('url')
    url = unquote(mail_url)
    print("GIVEN URL: ", url)
    pdf_name = preview.create(url)
    # ip_address = request.remote_addr
    result = 'Created PDF: <a href="{}"> Link to PDF </a>'.format(pdf_name)
    print(result)
    return render_template('preview-create.html', link=pdf_name)

@app.route('/preview-old')
def preview_page():
    mail_url = request.args.get('url')
    url = unquote(mail_url)
    return render_template('preview.html', mail_url=url)

@app.route('/loading')
def loading():
    return render_template('loading.html')

@app.route('/test', methods=['GET'])
def test():
    return render_template('test.html', url="google.com")


@app.route('/longtask', methods=['POST'])
def longtask():
    jsn = request.get_json()
    # data = request.data
    formdata = request.form.get('message')
    data = request.json
    task = long_task.apply_async()
    return jsonify({}), 202, {'Location': url_for('taskstatus',
                                                  _external=True,
                                                  _scheme='https',
                                                  task_id=task.id)}

@app.route('/create-preview-long', methods=['POST'])
def create_preview_long():
    url = request.form.get('url')
    task = create_preview_task.apply_async([url])
    return jsonify({}), 202, {'Location': url_for('taskstatus',
                                                  _external=True,
                                                  _scheme='https',
                                                  task_id=task.id)}

@app.route('/preview-pdf')
def pdf_preview():
    mail_url = request.args.get('url')
    url = unquote(mail_url)
    short_url = url.split('/')[-1]
    return render_template('pdf-preview.html', url=url, short_url=short_url)

## Celery

# @celery.task(bind=True)
# def long_task(self):
#     """Background task that runs a long function with progress reports."""
#     verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
#     adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
#     noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
#     message = ''
#     total = 100
#     for i in range(total):
#         self.update_state(state='PROGRESS',
#                           meta={'current': i, 'total': total,
#                                 'status': message})
#         time.sleep(1)
#     return { 'current': 100, 'total': 100, 'status': 'Task completed!', 'result': 42 }

# @celery.task(bind=True)
# def create_preview_task(self, url):
#     print("Task | url", url)
#     # url = 'https://cloud.mail.ru/public/2Lmu/4hWrXdAqo'
#     if(url[-1] != '/'):
#         url+='/'

#     total = 100
#     self.update_state(state='PROGRESS',
#                           meta={'current': 14, 'total': 100,
#                                 'status': 'Parsing page '})
#     names = preview.get_image_names(url)
#     self.update_state(state='PROGRESS',
#                           meta={'current': 28, 'total': total,
#                                 'status': 'Downloading images'})
#     imgs = preview.get_images_by_names(names)
#     self.update_state(state='PROGRESS',
#                           meta={'current': 32, 'total': total,
#                                 'status': 'Putting images into PDF'})
#     pdf_name = preview.imgs2pdf(imgs, url)
#     self.update_state(state='PROGRESS',
#                           meta={'current': 46, 'total': total,
#                                 'status': 'Converting pdf for adding frontend'})
#     nparr = preview.convert_pdf_to_cv2(pdf_name)
#     self.update_state(state='PROGRESS',
#                           meta={'current': 58, 'total': total,
#                                 'status': 'Adding frontend'})
#     path = preview.add_footer_and_header(nparr,pdf_name, len(imgs) )
#     self.update_state(state='PROGRESS',
#                           meta={'current': 72, 'total': total,
#                                 'status': 'Saving results'})
#     return { 'current': 100, 'total': 100, 'status': 'Задача выполнена!', 'result': path[1:] }



@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = create_preview_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)

@app.route('/e/<hashed>')
def encoded(hashed):
    decoded = base64.b64decode(hashed.encode('utf-8'))#.decode('utf-8') #cipher.decrypt(hashed)
    url = decoded.decode("utf-8") 
    names = preview.get_image_names(url)
    urls = preview.get_urls_by_names(names)
    encoded_url = "https://dndg.ru/e/" + hashed
    
    random.shuffle(urls)
    return render_template('web-preview.html', len=len(urls), images=urls, encoded_url=encoded_url)


@app.route('/preview')
def front():
    mail_url = request.args.get('url')
    url = unquote(mail_url)
    if(url[-1] != '/'):
        url+='/'
    path = base64.b64encode(url.encode('utf-8')).decode('utf-8')
    print(path)
    return redirect('/e/' +  path)