from python:3.11.11-alpine

COPY main.py local.cfg versions.yml ./

COPY ./requirements.txt ./

RUN python3 -m pip install -r requirements.txt

CMD ["python","main.py"]
