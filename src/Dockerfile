FROM python:3.13-slim

ADD . /code
ADD requirements.txt .
RUN pip install -r requirements.txt
CMD ["python", "/code/manet3-prom-exporter.py"]