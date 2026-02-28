import secrets
from datetime import datetime, timedelta, timezone
from models import Token, Security_logs
from app import db, mail
from flask_mail import Message
import re
from flask import render_template, request, has_request_context
from log_variables import SecurityAction, TokenAction, TokenError
from model_helper import utc_now_naive


def validate_token(token_str, expected_type: TokenAction):
    record = Token.query.filter_by(token=token_str).first()

    if not record:
        return None, TokenError.INVALID_TOKEN.value

    if record.type != expected_type.value:
        return None, TokenError.INVALID_TOKEN_TYPE.value

    if record.expire < utc_now_naive():
        db.session.delete(record)
        db.session.commit()
        return record, TokenError.TOKEN_EXPIRED.value

    return record, None


def create_security_logs(user, action):

    if isinstance(action, SecurityAction):
        action = action.value

    ip_address = None
    user_agent = None

    # AI (Chatgpt) assisted: Generated suggestion for capturing IP adress and user agent information beside action of the user.
    # ip adress and user agent concepts learned and applied.

    if has_request_context():
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.user_agent.string

    new_log = Security_logs(user_id = user.user_id, action=action,ip_address=ip_address,user_agent=user_agent)
    db.session.add(new_log)
    db.session.commit()

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

# def send_email(to, subject, body, html_body=None):
#     msg = Message(subject, recipients=[to])
#     msg.body = body
#     if html_body:
#         msg.html = html_body
#     mail.send(msg)


# AI (Chatgpt) assisted: To optimize the mail sending process and to create html content for the mails.
def send_email(to, subject, template_name, **kwargs):
    """
    Send an HTML email using a template.
    
    :param to: Receiver email
    :param subject: Mail title and HTML title
    :param template_name: .html folder in templates/email/  
    :param kwargs: function parameters to be used in the template
    """
    html_content = render_template(template_name, subject=subject, **kwargs)
    msg = Message(subject, recipients=[to], html=html_content)
    mail.send(msg)
    
def create_token(user, token_type, sys=False, hours_valid=1):

    if isinstance(token_type, TokenAction):
        token_type = token_type.value

    token_str = secrets.token_urlsafe(32)  # URL-safe
    created_at = utc_now_naive()

    if sys:
        expires_at = utc_now_naive() + timedelta(minutes=1)
    else:
        expires_at = utc_now_naive() + timedelta(hours=hours_valid)
    

    # If there is already a token with the same action type then override it, otherwise create new
    token_exist = Token.query.filter(Token.user_id==user.user_id, Token.type==token_type).first()
    if token_exist:
        db.session.delete(token_exist)

    #if user.token:
        #db.session.delete(user.token)
        # user.token.token = token_str
        # user.token.expire = expires_at
        # user.token.created_at = created_at
        # user.token.type = token_type
  
    new_token = Token(user_id=user.user_id, token=token_str, type=token_type, created_at=created_at ,expire=expires_at)
    db.session.add(new_token)

    db.session.commit()

    return token_str