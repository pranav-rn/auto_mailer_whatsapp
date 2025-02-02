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
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from email.message import EmailMessage
import smtplib
import json

app = Flask(__name__)

# Gemini API Configuration
GEMINI_API_KEY = "AIzaSyA2B1TFb2eO_abpAuZcRTt34mXetRR_AcA"

# Email configuration
EMAIL_USER = "pranavrajeshnarayan@gmail.com"
EMAIL_PASSWORD = "xeve cmgt zfgi flxr"  # Use an App Password, not your real Gmail password


def refine_email_content(content):
    """Refine email content using Gemini API."""
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [{"parts": [{"text": f"Refine this draft email and put name for regards as Pranav and skip the recepients name in the introduction and just put something formal: {content}"}]}]
    }

    # ✅ Correct API Endpoint
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

    try:
        response = requests.post(api_url, json=data, headers=headers)

        # Debugging: Print API response
        print("Response Status Code:", response.status_code)
        print("Response Text:", response.text)

        response_data = response.json()

        if "candidates" in response_data and len(response_data["candidates"]) > 0:
            return response_data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return "Error: Unexpected API response format."

    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"


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

user_email_data = {}

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

    # Parse the incoming message to extract recipient, subject, and content
    if "email" in incoming_msg.lower():
        parts = incoming_msg.split("content:", 1)
        
        if len(parts) == 2:
            recipient_and_subject = parts[0].strip()
            content = parts[1].strip()

            # Extract recipient and subject from the message
            recipient_match = re.search(r"to:\s*([\w\.-]+@[\w\.-]+)", recipient_and_subject)
            subject_match = re.search(r"subject:\s*(.*)", recipient_and_subject)
            
            if recipient_match and subject_match:
                recipient_email = recipient_match.group(1)
                subject = subject_match.group(1)
                
                # Refine the email content using the Gemini API
                refined_content = refine_email_content(content)
                
                # Send preview
                response.message(f"Email draft for review:\n\nSubject: {subject}\nTo: {recipient_email}\n\n{refined_content}\n\nReply with 'Send' to confirm.")
                
                # Store the email data temporarily (e.g., in a session or dictionary)
                user_number = request.values.get('From', '').strip()
                user_email_data[user_number] = (recipient_email, subject, refined_content)
                return str(response)
            else:
                response.message("Please provide both a valid recipient and subject in the format: 'to: email subject: subject content: content'")
                return str(response)

    elif "send" in incoming_msg.lower():
        # Retrieve stored email data
        user_number = request.values.get('From', '').strip()
        if user_number in user_email_data:
            recipient_email, subject, refined_content = user_email_data[user_number]
            send_email_with_attachment(recipient_email, subject, refined_content, media_filename)
            response.message("Email sent successfully with attachment.")
        else:
            response.message("No email draft found. Please provide email details first.")

        return str(response)

    else:
        response.message("Invalid command. Please provide email details in the format: 'email to: email subject: subject content: content'")
        return str(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))



