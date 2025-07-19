FROM python:3.9-slim

# Installa OpenSSL per generare i certificati
RUN apt-get update && apt-get install -y openssl

# Imposta la directory di lavoro
WORKDIR /app

# Copia il file dei requisiti e installa le dipendenze
COPY requirements.txt .

RUN pip3 install -r requirements.txt

# Copia il codice del microservizio
COPY microservice.py .

# Crea una directory per i certificati
RUN mkdir -p /certs

# Copia il file di configurazione OpenSSL
COPY openssl.cnf /certs/openssl.cnf

# Genera il certificato e la chiave privata con OpenSSL utilizzando il file di configurazione
RUN openssl req -x509 -newkey rsa:4096 -keyout /certs/server.key -out /certs/server.crt -days 365 -nodes -config /certs/openssl.cnf

# Esponi la porta 443 per HTTPS
EXPOSE 443

# Imposta la variabile di ambiente per il buffer Python
ENV PYTHONUNBUFFERED=1

# Avvia il server Flask con HTTPS usando i certificati generati
CMD ["python3", "microservice.py"]
