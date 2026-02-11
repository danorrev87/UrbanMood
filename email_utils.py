"""
Unified email sending that works with mailersend v0.x and v2.x.
"""
import logging

logger = logging.getLogger("urbanmood.email")

MAILERSEND_VERSION = None

def _detect_version():
    global MAILERSEND_VERSION
    if MAILERSEND_VERSION:
        return MAILERSEND_VERSION
    try:
        from mailersend.emails import NewEmail
        MAILERSEND_VERSION = "v0"
        logger.info("Detected mailersend v0.x (NewEmail API)")
    except (ImportError, ModuleNotFoundError):
        try:
            from mailersend import MailerSendClient, EmailBuilder
            MAILERSEND_VERSION = "v2"
            logger.info("Detected mailersend v2.x (MailerSendClient API)")
        except (ImportError, ModuleNotFoundError):
            MAILERSEND_VERSION = "unknown"
            logger.error("Could not detect mailersend version")
    return MAILERSEND_VERSION


def send_email(api_key, from_name, from_email, to_email, subject, html_content, to_name=None, reply_to=None):
    """Send an email using whichever mailersend version is installed."""
    if to_name is None:
        to_name = to_email

    version = _detect_version()
    logger.info("Sending email to=%s subject='%s' via mailersend %s", to_email, subject, version)

    if version == "v0":
        return _send_v0(api_key, from_name, from_email, to_email, to_name, subject, html_content, reply_to)
    elif version == "v2":
        return _send_v2(api_key, from_name, from_email, to_email, to_name, subject, html_content, reply_to)
    else:
        raise RuntimeError("mailersend library not found or unsupported version")


def _send_v0(api_key, from_name, from_email, to_email, to_name, subject, html_content, reply_to):
    from mailersend.emails import NewEmail as Email
    mailer = Email(api_key)
    mail_body = {}
    mailer.set_mail_from({"name": from_name, "email": from_email}, mail_body)
    mailer.set_mail_to([{"name": to_name, "email": to_email}], mail_body)
    mailer.set_subject(subject, mail_body)
    mailer.set_html_content(html_content, mail_body)
    if reply_to:
        mailer.set_reply_to(reply_to, mail_body)
    result = mailer.send(mail_body)
    logger.info("mailersend v0 response: %s", result)
    return result


def _send_v2(api_key, from_name, from_email, to_email, to_name, subject, html_content, reply_to):
    from mailersend import MailerSendClient, EmailBuilder
    client = MailerSendClient(api_key=api_key)
    builder = EmailBuilder()
    builder = builder.from_email(from_email, from_name)
    builder = builder.to(to_email, to_name)
    builder = builder.subject(subject)
    builder = builder.html(html_content)
    if reply_to:
        rto_email = reply_to.get("email", reply_to) if isinstance(reply_to, dict) else reply_to
        rto_name = reply_to.get("name", "") if isinstance(reply_to, dict) else ""
        if hasattr(builder, 'reply_to'):
            builder = builder.reply_to(rto_email, rto_name)
    email = builder.build()
    result = client.emails.send(email)
    logger.info("mailersend v2 response: %s", result)
    return result
