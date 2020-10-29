FROM python:3.8

WORKDIR /usr/src/app
COPY . .
RUN apt-get update
RUN apt-get install libgl1-mesa-glx libjpeg62
RUN pip install -r requirements.txt

ENV FLASK_APP app.py

CMD ["gunicorn", "-w", "4", "-b", ":5000", "--timeout","150", "app:app" ]
