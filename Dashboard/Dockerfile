FROM python:3

WORKDIR /usr/src/energymeter

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY dashboard.py ./

RUN touch .env
RUN echo $"is_docker=true" > .env

CMD ["python", "dashboard.py"]