FROM python:3.7

RUN mkdir /app
ADD . /app
WORKDIR /app

RUN pip install -r requirement.txt

CMD python /app/main.py