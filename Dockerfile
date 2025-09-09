FROM python:3.11-slim

WORKDIR /app
COPY app/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY app /app/app
ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["python", "-m", "app.main"]
