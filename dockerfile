# Dockerfile
FROM python:3.11-slim

# går inn i app mappen
WORKDIR /app

# Installerer requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#kopierer hele appen
COPY . .

# Slipper inn trafikk fra alle IP-adresser
ENV FLASK_RUN_HOST=0.0.0.0

#kjører kommandoen med "," som mellomrom
CMD ["flask", "run", "--host=0.0.0.0", "--port=5010"]