from python:3.11.11-alpine3.21

COPY main.py local.cfg versions.yml ./

ADD ./requirements.txt ./

RUN python3 -m pip install -r requirements.txt

CMD ["python","main.py"]
