FROM python:3.9.1
RUN mkdir -p /get_meter/bin ; \
  curl "https://www.modbusdriver.com/downloads/modpoll.tgz" | tar -xvzf - -C /get_meter/bin
RUN ln -s /get_meter/bin/modpoll/x86_64-linux-gnu/modpoll /get_meter/modpoll
ADD ./get_meter.py /get_meter/
ADD ./requirements.txt /get_meter/
WORKDIR /get_meter
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD [ "python3", "/get_meter/get_meter.py" ]
