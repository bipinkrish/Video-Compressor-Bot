FROM python:3-slim

WORKDIR /usr/src/app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY video.py video.py

EXPOSE 8080

CMD ["python", "video.py" ]
