from flask import Flask
from urllib.parse import unquote
from flask import request

import preview

app = Flask(__name__, static_url_path = "/static")

DOMAIN = 'http://18.218.160.207:5000'

@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/create-preview')
def create_preview():
    mail_url = request.args.get('url')
    url = unquote(mail_url)
    pdf_name = preview.create(url)
    ip_address = request.remote_addr
    print('Created PDF:', pdf_name)
    return 'Created PDF:      ' + DOMAIN + pdf_name[1:]