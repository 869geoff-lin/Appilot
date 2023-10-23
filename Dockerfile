FROM python:3.11-slim

WORKDIR /app

COPY . .
COPY ./bin /usr/local/bin/

RUN pip3 install -r requirements.txt

# CMD ["python3", "app.py"]
# CMD ["uvicorn", "app:app"]
ENTRYPOINT ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]