FROM tiangolo/meinheld-gunicorn:python3.7

LABEL maintainer="Vasyl Vaskul <basilboli@gmail.com>"

COPY ./tagli /app

RUN pip install -r requirements.txt


