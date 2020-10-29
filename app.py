from flask import Flask
from urllib.parse import unquote
from flask import request
import os

import preview

app = Flask(__name__, static_url_path = "/static")

DOMAIN = os.getenv('DOMAIN', 'http://localhost:5000')

@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/create-preview')
def create_preview():
    mail_url = request.args.get('url')
    url = unquote(mail_url)
    print("GIVEN URL: ", url)
    pdf_name = preview.create(url)
    ip_address = request.remote_addr
    print('Created PDF:', pdf_name)
    return 'Created PDF:      ' + DOMAIN + pdf_name[1:]