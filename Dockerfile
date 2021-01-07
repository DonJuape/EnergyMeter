FROM python:3.7-alpine

WORKDIR /usr/src/energymeter

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY energymeter.py ./

RUN touch .env
RUN echo $"is_docker=true"

CMD ["python", "energymeter.py"]