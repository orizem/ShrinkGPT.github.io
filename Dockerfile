FROM python:3.12.3

RUN pip install --upgrade pip

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . . 

EXPOSE 5000

CMD ["python", "main.py"]
