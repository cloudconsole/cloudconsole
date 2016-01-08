FROM ubuntu:14.04
MAINTAINER Ashok Raja <ashokraja.r@gmail.com>

RUN apt-get update && apt-get install -y python3 python3-pip \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3"]
CMD ["runserver.py"]
