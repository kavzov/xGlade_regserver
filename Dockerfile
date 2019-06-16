FROM python:3.6

COPY . /regserver

WORKDIR regserver

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:8000"]
