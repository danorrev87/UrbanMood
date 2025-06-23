from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from mailersend import emails
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

app = Flask(__name__)
# Allow CORS for the frontend, both local and deployed
CORS(app, resources={r"/send-email": {"origins": ["http://localhost:8000", "https://urbanmood.onrender.com"]}})

@app.route('/send-email', methods=['POST'])
def send_email():
    # Get API key from environment variable
    mailer_api_key = os.getenv("MAILERSEND_API_KEY")
    if not mailer_api_key:
        return jsonify({"success": False, "message": "MailerSend API key is not configured."}), 500

    # Get JSON data from the request
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Invalid JSON received."}), 400

    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    message = data.get('message')

    if not all([name, email, message]):
        return jsonify({"success": False, "message": "Missing required form fields."}), 400

    # Initialize MailerSend
    mailer = emails.NewEmail(mailer_api_key)

    # Define email parameters
    mail_body = {}
    mail_from = {
        "name": "Contacto UrbanMood",
        "email": "contacto@urbanmood.net", # Your verified "from" email
    }
    recipients = [
        {
            "name": "Danilo Orrego",
            "email": "dorrego@urbanmood.net",
        }
    ]
    
    reply_to = {
        "name": name,
        "email": email,
    }

    subject = f"Nuevo Contacto UrbanMood de {name}"
    html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nuevo Envío de Formulario de Contacto</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background-color: #1a1a1a;
            font-family: Arial, sans-serif;
        }}
        .container {{
            width: 100%;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #0D0D0D;
            color: #F2F2F2;
        }}
        .header {{
            background-color: #a8b720;
            padding: 20px;
            text-align: center;
            color: #0D0D0D;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .content {{
            padding: 30px 20px;
            border-top: 5px solid #a8b720;
        }}
        .content p {{
            font-size: 16px;
            line-height: 1.5;
            margin: 0 0 10px;
        }}
        .content strong {{
            color: #a8b720;
        }}
        .message-box {{
            background-color: #1a1a1a;
            border-left: 3px solid #a8b720;
            padding: 15px;
            margin-top: 20px;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            font-size: 12px;
            color: #3f484e;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>UrbanMood</h1>
        </div>
        <div class="content">
            <p><strong>Nuevo envío de formulario de contacto</strong></p>
            <hr style="border-color: #3f484e;">
            <p><strong>Nombre:</strong> {name}</p>
            <p><strong>Correo Electrónico:</strong> <a href="mailto:{email}" style="color: #a8b720;">{email}</a></p>
            <p><strong>Teléfono:</strong> {phone or 'No proporcionado'}</p>
            <div class="message-box">
                <p><strong>Mensaje:</strong></p>
                <p>{message}</p>
            </div>
        </div>
        <div class="footer">
            <p>&copy; 2024 UrbanMood. Todos los derechos reservados.</p>
        </div>
    </div>
</body>
</html>
    """

    try:
        # The setters populate the mail_body dictionary
        mailer.set_mail_from(mail_from, mail_body)
        mailer.set_mail_to(recipients, mail_body)
        mailer.set_subject(subject, mail_body)
        mailer.set_html_content(html_content, mail_body)
        mailer.set_reply_to(reply_to, mail_body)

        # Send the email. The library returns the response body as a string.
        # On success, the body is empty or contains a 202 status code. On failure, it contains an error message.
        api_response_body = mailer.send(mail_body)

        # The mailersend library returns different types on success (dict, empty string) vs failure (string with error).
        # A 202 status code is also a success indicator, which might be returned as a string or int.
        response_str = str(api_response_body).strip()

        if not response_str or response_str == '202' or isinstance(api_response_body, dict):
            return jsonify({"success": True, "message": "Email sent successfully!"})
        else:
            # If there's a different response body, it's an error from the API
            print(f"Failed to send email. MailerSend API response: {api_response_body}")
            return jsonify({"success": False, "message": "Failed to send email."}), 500

    except Exception as e:
        # This will catch exceptions within the Python code itself
        print(f"An error occurred while sending email: {e}")
        return jsonify({"success": False, "message": "An error occurred while sending the email."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001) # Runs on a different port than the http.server
