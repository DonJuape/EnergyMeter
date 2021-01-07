FROM arm32v7/python:3.7-buster

WORKDIR /usr/src/energymeter

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN pip3 install RPi.GPIO

COPY energymeter.py ./

RUN touch .env
RUN echo $"is_docker=true" > .env

CMD ["python", "energymeter.py"]