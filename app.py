from flask import Flask, request, jsonify, send_from_directory, render_template, redirect
from flask_cors import CORS
import os
import logging
from db import Base, engine
from config import config as app_config
from routes.auth import auth_bp
from routes.admin import admin_bp
try:
    from mailersend.emails import NewEmail as Email
except ImportError:
    from mailersend import Email
from dotenv import load_dotenv
from flask import session

load_dotenv() # Load environment variables from .env file

app = Flask(__name__, static_folder='static', template_folder='templates')
# Load core config (SECRET_KEY etc.)
app.secret_key = app_config.SECRET_KEY  # ensure session works
app.config.setdefault('SESSION_COOKIE_SAMESITE', 'Lax')
app.config.setdefault('SESSION_COOKIE_HTTPONLY', True)

# Logging configuration (idempotent if gunicorn already sets handlers)
if not logging.getLogger().handlers:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger("urbanmood")

# Allow CORS for the frontend, both local and deployed
allowed_origins = [
    "http://localhost:8000",
    "http://localhost:5001",
    "https://urbanmood.onrender.com",
    "https://urbanmood.net"
]
CORS(app, resources={r"/send-email": {"origins": allowed_origins}})

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)

# Ensure tables exist (for early dev; later replace with Alembic migrations)
with engine.begin() as conn:
    Base.metadata.create_all(conn)

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
    mailer = Email(mailer_api_key)

    # Define email parameters
    mail_body = {}
    mail_from = {
        "name": "Contacto UrbanMood",
        "email": "urbanmoodfitness@gmail.com", # Updated verified from email
    }
    recipients = [
        {
            "name": "Danilo Orrego",
            "email": "urbanmoodfitness@gmail.com",
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
        logger.exception("Error while sending email")
        return jsonify({"success": False, "message": "An error occurred while sending the email."}), 500

@app.route('/health')
def health():
    """Simple healthcheck for uptime monitoring."""
    return jsonify({"status": "ok"})

@app.route('/')
def index():
    if session.get('uid'):
        if session.get('role') == 'admin':
            return redirect('/admin/users')
        return redirect('/mi-rutina')
    return render_template('index.html')

@app.context_processor
def inject_session_flags():
    return {
        'logged_in': bool(session.get('uid')),
        'user_role': session.get('role')
    }

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

@app.after_request
def add_security_headers(response):
    # Basic security & caching headers for static assets
    response.headers.setdefault('X-Content-Type-Options', 'nosniff')
    response.headers.setdefault('X-Frame-Options', 'SAMEORIGIN')
    response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
    # Light caching: cache static assets (not root HTML) for 1 day
    if request.path.startswith('/static/'):
        response.headers.setdefault('Cache-Control', 'public, max-age=86400, immutable')
    return response

if __name__ == '__main__':
    debug = os.getenv('FLASK_DEBUG', '').lower() in ('1', 'true', 'yes')
    port = int(os.getenv('PORT', '5001'))
    logger.info("Starting development server on port %s (debug=%s)", port, debug)
    app.run(debug=debug, host='0.0.0.0', port=port)
