FROM python:3.8

WORKDIR /usr/src/app
COPY . .
RUN apt-get update
RUN apt-get install 'ffmpeg'\
    'libsm6'\ 
    'libxext6'  -y
RUN pip install -r requirements.txt

CMD ["./run-redis.sh"]

# RUN ./run-redis.sh

CMD ["celery", "-A", "app.celery", "worker", "--loglevel=info"]
# RUN celery -A app.celery worker --loglevel=info

ENV FLASK_APP app.py

CMD ["gunicorn", "-w", "5", "--worker-class", "gevent", "-b", ":5000", "--timeout","120", "app:app" ]
