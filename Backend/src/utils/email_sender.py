import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio
from pathlib import Path

# Get email settings from environment
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
DEFAULT_SENDER = os.getenv('DEFAULT_SENDER')

async def send_podcast_email(
    recipient_email: str,
    audio_file_path: str,
    transcript: dict,
    is_anchor: bool = False
) -> bool:
    try:
        if not all([SMTP_USERNAME, SMTP_PASSWORD]):
            raise ValueError("Email credentials not configured")

        # Create message
        msg = MIMEMultipart()
        msg['From'] = DEFAULT_SENDER
        msg['To'] = recipient_email
        msg['Subject'] = "Your AI Generated " + ("News Broadcast" if is_anchor else "Podcast")

        # Add body
        body = f"""
        Hello!

        Your AI-generated audio content is ready.

        Summary:
        {transcript.get('scriptNotes', '') if is_anchor else transcript.get('scratchpad', '')}

        Best regards,
        AI Podcast Generator
        """
        msg.attach(MIMEText(body, 'plain'))

        # Attach audio file
        with open(audio_file_path, 'rb') as audio_file:
            audio_data = audio_file.read()
            audio_attachment = MIMEAudio(audio_data, _subtype="wav")
            audio_attachment.add_header(
                'Content-Disposition',
                'attachment',
                filename=Path(audio_file_path).name
            )
            msg.attach(audio_attachment)

        # Connect and send
        print(f"Connecting to SMTP server: {SMTP_SERVER}:{SMTP_PORT}")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            print(f"Logging in as: {SMTP_USERNAME}")
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            print(f"Sending email to: {recipient_email}")
            server.send_message(msg)

        print(f"Email sent successfully to {recipient_email}")
        return True

    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False