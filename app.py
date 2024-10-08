from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_cors import CORS
import json
import qrcode
from io import BytesIO
from email.mime.image import MIMEImage

app = Flask(__name__)
CORS(app)

# Función genérica para enviar correos electrónicos con opción de adjuntar una imagen (QR)
def send_email(receiver_email, subject, body, qr_img_data=None):
    sender_email = "digitallstarken@gmail.com"  # Reemplaza con tu correo
    password = "hjpn cklo qqhg tlme"  # Reemplaza con tu contraseña o app password

    # Configurar el mensaje MIME
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    # Adjuntar el cuerpo del mensaje en formato HTML
    part = MIMEText(body, "html")
    msg.attach(part)

    # Si hay una imagen QR para adjuntar
    if qr_img_data:
        img_part = MIMEImage(qr_img_data.getvalue())
        img_part.add_header('Content-Disposition', 'attachment', filename="qrcode.png")
        msg.attach(img_part)

    # Enviar el correo
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("Correo enviado exitosamente")
    except Exception as e:
        print(f"Error enviando el correo: {e}")

# Ruta para procesar la donación y enviar el correo de procesamiento
@app.route('/submit_donation', methods=['POST'])
def submit_donation():
    data = request.get_json()

    email = data.get('email')
    if not email:
        return jsonify({'error': 'Email es requerido'}), 400

    # Enviar el correo de procesamiento de pago
    subject = "Tu pago está siendo procesado"
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color: #4CAF50;">¡Hola {data['name']}!</h2>
            <p>Queremos informarte que tu pago está siendo procesado.</p>
            <p><strong>El equipo de Starken</strong></p>
        </body>
    </html>
    """

    send_email(email, subject, body)

    return jsonify({'message': 'Correo de procesamiento enviado correctamente'}), 200

# Ruta para enviar el correo de agradecimiento con el QR adjunto
@app.route('/send_thank_you_email', methods=['POST'])
def send_thank_you_email():
    data = request.get_json()

    email = data.get('email')
    participation_code = data.get('participationCode')
    
    if not email:
        return jsonify({'error': 'Email es requerido'}), 400

    subject = "Gracias por tu aporte en Starken"
    body = f"""
    <html>
        <body>
            <h2>¡Gracias por tu apoyo!</h2>
            <p>Tu pago ha sido procesado con éxito.</p>
            <p>Tu código de participación es: {participation_code}</p>
        </body>
    </html>
    """

    # Crear un código QR
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(participation_code)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    # Convertir la imagen a un buffer para enviarla por email
    buffer = BytesIO()
    img.save(buffer)
    buffer.seek(0)

    # Enviar el correo con el QR adjunto
    send_email(email, subject, body, qr_img_data=buffer)

    return jsonify({'message': 'Correo de agradecimiento enviado correctamente con QR'}), 200


if __name__ == '__main__':
    app.run(debug=True)
