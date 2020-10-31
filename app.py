from flask import Flask, request, render_template, session, flash, redirect, \
    url_for, jsonify
from celery import Celery
from urllib.parse import unquote
import os
import time
import preview

DOMAIN = os.getenv('DOMAIN', 'http://localhost:5000')
REDIS_URL = os.getenv('REDIS_URL', 'localhost')

app = Flask(__name__, static_url_path = "/static")
app.config['SECRET_KEY'] = 'top-secret!'

# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://' + REDIS_URL + ':6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://' + REDIS_URL + ':6379/0'

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/create-preview')
def create_preview():
    mail_url = request.args.get('url')
    url = unquote(mail_url)
    print("GIVEN URL: ", url)
    pdf_name = preview.create(url)
    # ip_address = request.remote_addr
    result = 'Created PDF: <a href="{}"> Link to PDF </a>'.format(pdf_name)
    print(result)
    return render_template('preview-create.html', link=pdf_name)

@app.route('/preview')
def preview_page():
    mail_url = request.args.get('url')
    url = unquote(mail_url)
    return render_template('preview.html', mail_url=url)

@app.route('/test')
def test():
    return render_template('loading.html')


@app.route('/longtask', methods=['POST'])
def longtask():
    jsn = request.get_json()
    # data = request.data
    data = request.json
    print('get jsn', jsn)
    print('get data', data)
    task = long_task.apply_async()
    return jsonify({}), 202, {'Location': url_for('taskstatus',
                                                  task_id=task.id)}

@app.route('/create-preview-long', methods=['POST'])
def create_preview_long():
    # jsn = request.get_json()
    # data = request.data
    # data = request.json
    # print('get jsn', jsn)
    # print('get data', data)
    task = create_preview_task.apply_async()
    return jsonify({}), 202, {'Location': url_for('taskstatus',
                                                  task_id=task.id)}

## Celery

@celery.task(bind=True)
def long_task(self):
    """Background task that runs a long function with progress reports."""
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = ''
    total = 100
    for i in range(total):
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': total,
                                'status': message})
        time.sleep(1)
    return { 'current': 100, 'total': 100, 'status': 'Task completed!', 'result': 42 }

@celery.task(bind=True)
def create_preview_task(self):
    url = 'https://cloud.mail.ru/public/2Lmu/4hWrXdAqo'
    if(url[-1] != '/'):
        url+='/'

    total = 100
    self.update_state(state='PROGRESS',
                          meta={'current': 14, 'total': 100,
                                'status': 'Parsing page '})
    names = preview.get_image_names(url)
    self.update_state(state='PROGRESS',
                          meta={'current': 28, 'total': total,
                                'status': 'Downloading images'})
    imgs = preview.get_images_by_names(names)
    self.update_state(state='PROGRESS',
                          meta={'current': 32, 'total': total,
                                'status': 'Putting images into PDF'})
    pdf_name = preview.imgs2pdf(imgs, url)
    self.update_state(state='PROGRESS',
                          meta={'current': 46, 'total': total,
                                'status': 'Converting pdf for adding frontend'})
    nparr = preview.convert_pdf_to_cv2(pdf_name)
    self.update_state(state='PROGRESS',
                          meta={'current': 58, 'total': total,
                                'status': 'Adding frontend'})
    path = preview.add_footer_and_header(nparr,pdf_name, len(imgs) )
    self.update_state(state='PROGRESS',
                          meta={'current': 72, 'total': total,
                                'status': 'Saving results'})
    return { 'current': 100, 'total': 100, 'status': 'Task completed!', 'result': path }



@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = long_task.AsyncResult(task_id)
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