FROM python:3.8

WORKDIR /usr/src/app
COPY . .
RUN apt-get update
RUN apt-get install 'ffmpeg'\
    'libsm6'\ 
    'libxext6'  -y
RUN pip install -r requirements.txt

ENV FLASK_APP app.py

CMD ["gunicorn", "-w", "4", "-b", ":5000", "--timeout","500", "app:app" ]
