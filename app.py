'''import os
import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import smtplib
from email.message import EmailMessage

app = Flask(__name__)

# DeepSeek API configuration
DEEPSEEK_API_ENDPOINT = "https://api.deepseek.ai/refine"
DEEPSEEK_API_KEY = "your_deepseek_api_key"

# Email configuration
EMAIL_USER = "pranavrajeshnarayan@gmail.com"
EMAIL_PASSWORD = "xeve cmgt zfgi flxr"  # For Gmail, use App Passwords, not your real password


def refine_email_content(content):
    """Refine email content using DeepSeek API."""
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
    data = {"text": content}
    response = requests.post(DEEPSEEK_API_ENDPOINT, json=data, headers=headers)
    return response.json().get("refined_text", "Error refining content")


def send_email_with_attachment(to_email, subject, body, attachment_path=None):
    """Send an email with an optional attachment."""
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = to_email
    msg.set_content(body)
    
    # Attach file if provided
    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, 'rb') as f:
            file_data = f.read()
            file_name = os.path.basename(attachment_path)
            msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)
    
    # Send the email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASSWORD)
        smtp.send_message(msg)


@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    incoming_msg = request.values.get('Body', '').strip()
    media_url = request.values.get('MediaUrl0')  # Handle the first media attachment if any
    media_filename = None

    response = MessagingResponse()

    if media_url:
        # Download attachment
        media_response = requests.get(media_url)
        media_filename = "attachment_received"
        with open(media_filename, "wb") as f:
            f.write(media_response.content)

    if "draft email" in incoming_msg.lower():
        recipient = "recipient@example.com"
        subject = "Your Subject Here"
        content = incoming_msg.split(":")[1] if ":" in incoming_msg else "Draft content missing."
        
        refined_content = refine_email_content(content)
        
        response.message(f"Email draft for review:\n\nSubject: {subject}\nTo: {recipient}\n\n{refined_content}\n\nReply with 'Send' to confirm.")
        return str(response)

    elif "send" in incoming_msg.lower():
        send_email_with_attachment("recipient@example.com", "Your Subject Here", refined_content, media_filename)
        response.message("Email sent successfully with attachment.")
        return str(response)

    else:
        response.message("Invalid command. Use 'Draft email: content'")
        return str(response)


if __name__ == "__main__":
    app.run()'''



import os
import requests
import re
import json
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from email.message import EmailMessage
import smtplib
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import firebase_admin
from firebase_admin import credentials, firestore
import mimetypes

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Firebase configuration
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")
cred = credentials.Certificate(json.loads(FIREBASE_CREDENTIALS))
firebase_admin.initialize_app(cred)
db = firestore.client()

# Encryption key (should be securely stored and rotated periodically)
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
fernet = Fernet(ENCRYPTION_KEY)

def encrypt(data):
    return fernet.encrypt(data.encode()).decode()

def decrypt(data):
    return fernet.decrypt(data.encode()).decode()

def store_user_credentials(user_id, email, password, api_key):
    encrypted_data = {
        "email": encrypt(email),
        "password": encrypt(password),
        "api_key": encrypt(api_key)
    }
    db.collection("users").document(user_id).set(encrypted_data)

def get_user_credentials(user_id):
    doc = db.collection("users").document(user_id).get()
    if doc.exists:
        data = doc.to_dict()
        return {
            "email": decrypt(data["email"]),
            "password": decrypt(data["password"]),
            "api_key": decrypt(data["api_key"])
        }
    return None

def refine_email_content(content, api_key):
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": f"Refine this draft email, add regards but dont put a placeholder for the name, and never leave a placeholder for any name. If you don't know who the email is for, just write something gender-neutral or generic: {content}"}]}]
    }
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    try:
        response = requests.post(api_url, json=data, headers=headers)
        response_data = response.json()
        if "candidates" in response_data:
            return response_data["candidates"][0]["content"]["parts"][0]["text"]
        return "Error: Unexpected API response format."
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

def send_email(to_email, subject, body, user_email, user_password, attachment_paths=None):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = user_email
    msg['To'] = to_email
    msg.set_content(body)

    # Attach all files
    if attachment_paths:
        for path in attachment_paths:
            if os.path.exists(path):
                mime_type, _ = mimetypes.guess_type(path)
                if not mime_type:
                    mime_type = "application/octet-stream"
                main_type, sub_type = mime_type.split('/', 1)

                with open(path, 'rb') as f:
                    file_data = f.read()
                
                msg.add_attachment(file_data, maintype=main_type, subtype=sub_type, filename=os.path.basename(path))


    # Send email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(user_email, user_password)
        smtp.send_message(msg)

user_email_data = {}

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    incoming_msg = request.values.get('Body', '').strip()
    user_id = request.values.get('From', '').strip()
    attachment_paths = []

    response = MessagingResponse()

    # Handle multiple attachments
    num_media = int(request.values.get('NumMedia', 0))
    for i in range(num_media):
        media_url = request.values.get(f'MediaUrl{i}')
        media_content_type = request.values.get(f'MediaContentType{i}')
        if media_url and media_content_type:
            ext = mimetypes.guess_extension(media_content_type) or ".bin"
            file_path = f"attachment_{i}{ext}"
            media_response = requests.get(media_url)
            with open(file_path, "wb") as f:
                f.write(media_response.content)
            attachment_paths.append(file_path)

    if incoming_msg.lower().startswith("register"):
        parts = incoming_msg.split()
        if len(parts) == 4:
            email, password, api_key = parts[1], parts[2], parts[3]
            store_user_credentials(user_id, email, password, api_key)
            response.message("Registration successful! You can now send emails.")
        else:
            response.message("Invalid format. Use: register <email> <app_password> <gemini_api_key>")
        return str(response)

    credentials = get_user_credentials(user_id)
    if not credentials:
        response.message("You are not registered. Use 'register <email> <app_password> <gemini_api_key>' to register.")
        return str(response)

    if "email" in incoming_msg.lower():
        parts = incoming_msg.split("content:", 1)
        if len(parts) == 2:
            recipient_and_subject = parts[0].strip()
            content = parts[1].strip()
            recipient_match = re.search(r"to:\s*([\w\.-]+@[\w\.-]+)", recipient_and_subject)
            subject_match = re.search(r"subject:\s*(.*)", recipient_and_subject)

            if recipient_match and subject_match:
                recipient_email = recipient_match.group(1)
                subject = subject_match.group(1)
                refined_content = refine_email_content(content, credentials['api_key'])
                user_email_data[user_id] = (recipient_email, subject, refined_content, attachment_paths)
                response.message(f"Email draft for review:\n\nSubject: {subject}\nTo: {recipient_email}\n\n{refined_content}\n\nReply with 'Send' to confirm.")
                return str(response)
            else:
                response.message("Invalid format. Use: email to: email subject: subject content: content")
                return str(response)

    elif "send" in incoming_msg.lower():
        if user_id in user_email_data:
            recipient_email, subject, refined_content, attachment_paths = user_email_data[user_id]
            send_email(recipient_email, subject, refined_content, credentials['email'], credentials['password'], attachment_paths)
            response.message("Email sent successfully with all attachments.")
        else:
            response.message("No email draft found. Please provide email details first.")
        return str(response)

    response.message("Invalid command. Use 'register <email> <app_password> <gemini_api_key>' to register.")
    return str(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
