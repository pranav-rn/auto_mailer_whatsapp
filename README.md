# AutoMailer

AutoMailer is an automated email-sending bot that integrates with Twilio's WhatsApp API to receive requests and send emails using user-specified credentials.

## Features
- Receive email-sending requests via WhatsApp.
- Securely store user credentials in Firebase Firestore with encryption.
- Send emails using SMTP with support for attachments.
- Temporarily store email attachments in Firebase Storage.
- Automatically delete attachments after sending for privacy.

## Tech Stack
- **Backend:** Python (Flask/FastAPI)
- **Database:** Firebase Firestore
- **Storage:** Firebase Storage
- **Messaging API:** Twilio WhatsApp API
- **Email:** SMTP (Gmail, Outlook, etc.)
- **Hosting:** Render

## Setup
### Prerequisites
- Python 3.x
- Firebase project set up with Firestore and Storage
- Twilio account with WhatsApp API enabled

### Installation
```sh
# Clone the repository
git clone https://github.com/pranav-rn/auto_mailer_whatsapp.git
cd auto_mailer_whatsapp

# Install dependencies
pip install -r requirements.txt
```

### Firebase Setup
1. Create a Firebase project.
2. Enable Firestore and Firebase Storage.
3. Download `serviceAccountKey.json` and place it in the project root.
4. Add Firestore security rules to restrict access.

### Twilio Sandbox Setup
To use Twilio's WhatsApp API, follow these steps to set up the sandbox:
1. Sign in to your Twilio account.
2. Go to **Messaging** > **Try It Out** > **Send a WhatsApp Message**.
3. Follow the instructions to join the Twilio WhatsApp sandbox by sending a designated message to a provided Twilio number.
4. Once joined, you can use the sandbox number to send and receive messages during development.

### Environment Variables
Create a `.env` file and add:
```env
FIREBASE_CREDENTIALS=serviceAccountKey.json
ENCRYPTION_KEY=your_secure_encryption_key
```

## WhatsApp Message Format
### Registering a User
To register an email account for sending emails, send a message in the following format:
```
register <your email id> <app password with no spaces> <gemini api key>
```
Your credentials will be securely stored in Firebase Firestore with encryption.

### Sending an Email
To send an email using WhatsApp, send a message in the following format:
```
email to: <recepients email> subject: <subject> content: <body of the mail>
```
For attachments, upload the file first and send the email request with the filename specified in the message.

## Running the Bot
```sh
python app.py
```

## Deployment
1. Deploy the app to [Render](https://render.com/) or another hosting platform.
2. Set up environment variables in Render's dashboard.
3. Update Twilio's webhook URL to point to your deployed app.

## Security Considerations
- **Encryption:** User credentials are stored in Firestore with encryption.
- **Attachment Handling:** Attachments are deleted after emails are sent.
- **Access Control:** Firebase security rules restrict unauthorized access.

## License
MIT License

## Contributing
Pull requests are welcome! For major changes, please open an issue first.

## Contact
For questions, reach out via [GitHub Issues](https://github.com/pranav-rn/auto_mailer_whatsapp/issues).
