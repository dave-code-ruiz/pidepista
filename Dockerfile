# Utiliza una imagen base de Python
FROM python:3.9-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de tu proyecto en el contenedor
COPY . .

# Instala las dependencias necesarias
RUN pip install flask bcrypt

# Expone el puerto en el que se ejecutar� la aplicaci�n
EXPOSE 5000

# Define el comando para ejecutar la aplicaci�n
CMD ["python", "app.py"]
