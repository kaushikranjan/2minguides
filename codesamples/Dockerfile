from apache/spark:3.5.3-python3

USER root

WORKDIR /opt/application

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ src/
COPY runners/ .

RUN chmod -R 777 /opt/application
