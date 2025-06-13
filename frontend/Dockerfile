# Dockerfile para el Frontend (HTML/JS)
# Usa la imagen oficial de Nginx basada en Alpine por su ligereza y eficiencia.
FROM nginx:alpine

# Elimina el archivo index.html predeterminado de Nginx si existe.
# La imagen oficial Nginx sirve por defecto desde /usr/share/nginx/html/.
RUN rm -f /usr/share/nginx/html/index.html

# Copia tu archivo index.html personalizado a la ubicación donde Nginx lo sirve.
# Asegúrate de que 'index.html' esté en el mismo directorio que este Dockerfile.
COPY index.html /usr/share/nginx/html/index.html

# Nginx ya está configurado para escuchar en el puerto 80 por defecto.
# EXPOSE 80 (esta instrucción es más que todo documentación, Nginx ya lo gestiona)