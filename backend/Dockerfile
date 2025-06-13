# Dockerfile para el Backend (Aplicación Flask)
# Usa una imagen oficial de Python ligera basada en Debian.
FROM python:3.9-slim-buster

# Establece el directorio de trabajo dentro del contenedor.
WORKDIR /app

# Copia el archivo de requisitos e instala las dependencias de Python.
# Esto se hace en un paso separado para aprovechar la caché de Docker:
# si requirements.txt no cambia, Docker no reinstalará las dependencias.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación al directorio de trabajo.
COPY . .

# Expone el puerto en el que la aplicación Flask escuchará.
EXPOSE 5000

# Comando para ejecutar la aplicación Flask cuando el contenedor se inicie.
# Se utiliza la forma de array JSON para un mejor manejo de señales del sistema.
# Para producción, se recomienda usar un servidor WSGI como Gunicorn (ej: CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]).
CMD ["python", "app.py"]