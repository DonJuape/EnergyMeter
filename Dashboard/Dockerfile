FROM python:3

WORKDIR /usr/src/energymeter

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY dashboard.py ./

ENV is_docker=true

CMD ["python", "dashboard.py"]