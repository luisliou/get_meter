FROM python:3.9.1
RUN mkdir /get_meter/ ; \
  curl "https://www.modbusdriver.com/downloads/modpoll.tgz" | tar -xvzf - -C /get_meter
ADD ./get_meter.py /get_meter/
ADD ./requirements.txt /get_meter/
WORKDIR /get_meter
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD [ "python3", "/get_meter/get_meter.py" ]
