from flask import Flask, request, jsonify
from flask_cors import CORS # Para manejar las políticas de seguridad entre dominios
import os
import smtplib # Para enviar correos electrónicos
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import mimetypes # Para detectar el tipo MIME de los archivos adjuntos
from dotenv import load_dotenv # Para cargar variables de entorno (recomendado)

# Cargar variables de entorno desde un archivo .env (para desarrollo local)
# En producción, se recomienda configurar estas variables directamente en el entorno del servidor
# (ej. en AWS ECS/EC2, Kubernetes, etc.) para mayor seguridad.
load_dotenv()

app = Flask(__name__)
# Habilitar CORS para permitir peticiones desde cualquier origen (ej. tu frontend).
# En un entorno de producción real, DEBES restringir esto a los dominios de tu frontend.
# Ejemplo: CORS(app, origins=["http://tu-dominio-frontend.com"])
CORS(app)

# --- Configuración del Servidor SMTP ---
# ¡IMPORTANTE! NUNCA GUARDES ESTAS CREDENCIALES DIRECTAMENTE EN EL CÓDIGO FUENTE EN PRODUCCIÓN.
# Usa siempre variables de entorno. Aquí usamos os.getenv() que las lee de .env o del sistema.
EMAIL_USER = os.getenv('EMAIL_USER', 'tu_correo_de_envio@gmail.com') # <--- REEMPLAZA ESTO
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'tu_contraseña_de_aplicacion_gmail') # <--- REEMPLAZA ESTO

# Para Gmail, necesitas una "contraseña de aplicación" generada en la configuración de seguridad de tu cuenta de Google,
# NO tu contraseña de Gmail habitual.
# Ve a tu cuenta de Google > Seguridad > Contraseñas de aplicación.
# Si usas otro proveedor (Outlook, Yahoo, tu propio servidor SMTP), las configuraciones serán diferentes.

SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587)) # 587 para STARTTLS, 465 para SSL

@app.route('/send-photo', methods=['POST'])
def send_photo():
    # Validar que se hayan recibido los campos necesarios
    if 'email' not in request.form:
        return jsonify({"message": "Correo electrónico destino no proporcionado."}), 400
    if 'photo' not in request.files:
        return jsonify({"message": "No se ha seleccionado ninguna foto."}), 400

    recipient_email = request.form['email']
    photo = request.files['photo']

    # Validar que el archivo de foto no esté vacío
    if not photo.filename:
        return jsonify({"message": "Nombre de archivo de foto inválido o archivo vacío."}), 400

    try:
        # Crear el mensaje de correo multipart (para adjuntar archivos)
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = recipient_email
        msg['Subject'] = "Foto enviada desde tu aplicación web"

        # Añadir un cuerpo de texto simple al correo (obligatorio para algunos clientes)
        # Puedes añadir un mensaje HTML si quieres: msg.attach(MIMEText('<p>¡Hola! Aquí tienes la foto enviada desde la app.</p>', 'html'))
        # msg.attach(MIMEText("Adjunto la foto enviada desde la aplicación web.", 'plain', 'utf-8'))

        # Adjuntar la foto
        # Crear un objeto MIMEBase para el adjunto
        part = MIMEBase('application', 'octet-stream')
        # Leer el contenido binario de la foto
        part.set_payload(photo.read())

        # Intentar adivinar el tipo MIME del archivo a partir de su extensión
        content_type, encoding = mimetypes.guess_type(photo.filename)
        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream' # Fallback si no se puede adivinar
        
        # Separar el tipo MIME en tipo principal (ej. image) y subtipo (ej. jpeg)
        maintype, subtype = content_type.split('/', 1)
        part = MIMEBase(maintype, subtype)
        
        # Volver a leer el payload ya que photo.read() lo consume una vez.
        # Es más eficiente manejar photo.stream.read() si el archivo es grande.
        # Para archivos pequeños, photo.read() dos veces funciona, pero lo ideal es resetear el stream o guardarlo en una variable.
        # Para simplificar este ejemplo, asumo photo.read() solo se hace una vez.
        # Una mejor práctica sería: photo_data = photo.read() y luego part.set_payload(photo_data)
        photo.seek(0) # Esto resetea el puntero del archivo al inicio para leerlo de nuevo
        part.set_payload(photo.read())


        # Codificar el payload a Base64 (estándar para adjuntos de correo)
        encoders.encode_base64(part)
        
        # Añadir cabeceras para el nombre del archivo adjunto
        part.add_header('Content-Disposition', f'attachment; filename="{photo.filename}"')
        
        # Adjuntar la parte de la foto al mensaje principal
        msg.attach(part)

        # Enviar el correo usando SMTP
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls() # Habilitar cifrado TLS (Transport Layer Security)
            server.login(EMAIL_USER, EMAIL_PASSWORD) # Autenticarse en el servidor SMTP
            server.sendmail(EMAIL_USER, recipient_email, msg.as_string()) # Enviar el correo

        return jsonify({"message": "Foto enviada exitosamente!"}), 200

    except smtplib.SMTPAuthenticationError:
        # Error si las credenciales de correo son incorrectas
        print("Error de autenticación SMTP. Revisa tu usuario y contraseña de aplicación.")
        return jsonify({"message": "Error de autenticación SMTP. Revisa las credenciales del servidor o tu contraseña de aplicación."}), 500
    except smtplib.SMTPConnectError:
        # Error si no se puede conectar al servidor SMTP (dirección o puerto incorrectos, firewall)
        print("Error de conexión SMTP. Revisa la dirección del servidor y el puerto.")
        return jsonify({"message": "Error de conexión SMTP. Revisa la configuración del servidor (SMTP_SERVER, SMTP_PORT) o tu conexión a internet."}), 500
    except Exception as e:
        # Cualquier otro error inesperado
        print(f"Error general al enviar correo: {e}")
        return jsonify({"message": f"Error interno del servidor: {str(e)}"}), 500

if __name__ == '__main__':
    # Ejecuta la aplicación Flask en modo de depuración.
    # 'host=0.0.0.0' hace que la aplicación sea accesible desde cualquier IP (necesario en Docker).
    # 'port=5000' es el puerto donde Flask escuchará las peticiones.
    app.run(debug=True, host='0.0.0.0', port=5000)
