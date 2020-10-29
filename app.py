from flask import Flask, render_template
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
    result = 'Created PDF: <a href="{}"> Link to PDF </a>'.format(pdf_name)
    print(result)
    return result

@app.route('/preview')
def preview_page():
    mail_url = request.args.get('url')
    url = unquote(mail_url)
    return render_template('preview.html', mail_url=url)