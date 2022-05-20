FROM python:3.7.4

WORKDIR /app

COPY requirment.txt requirment.txt
RUN pip install -r requirment.txt

COPY . . 

CMD ["python","manage.py","runserver","0.0.0.0:8000"]