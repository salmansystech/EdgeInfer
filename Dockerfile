FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py server.py ./
COPY src ./src

EXPOSE 5000

CMD ["flask", "--app", "server", "run", "--host=0.0.0.0", "--port=5000"]
