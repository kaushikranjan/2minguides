from apache/spark:3.5.4-python3

USER root

WORKDIR /opt/application

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY runners/ .

RUN chmod -R 777 /opt/application
