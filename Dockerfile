FROM python:3.10-slim-buster

WORKDIR /app
COPY . /app 

RUN apt-get update -y && apt-get install -y awscli && rm -rf /var/lib/apt/lists/*

RUN apt-get update && pip install -r requirements.txt
CMD ["python3", "app.py"]


