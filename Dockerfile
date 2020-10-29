FROM python:3.8

WORKDIR /usr/src/app
COPY . .
RUN apt-get install libgl1-mesa-glx
RUN pip install -r requirements.txt

ENV FLASK_APP app.py

CMD ["gunicorn", "-w", "4", "-b", ":5000", "--timeout","150", "app:app" ]
