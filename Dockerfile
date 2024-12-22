FROM ubuntu:20.04
        
RUN apt update
RUN apt-get install -y python3.6 python3-pip python3-dev build-essential gcc \
    libsnmp-dev snmp-mibs-downloader

RUN pip3 install --upgrade pip

RUN mkdir /app
WORKDIR /app
COPY . /app

WORKDIR /app/
RUN pip3 install -r requirements.txt

WORKDIR /app/
CMD python3 info1.py

WORKDIR /app/
CMD python3 info2.py

WORKDIR /app/
CMD python3 info3.py

WORKDIR /app/
CMD python3 info4.py

