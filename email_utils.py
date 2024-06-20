import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Function to send an email
def sendNotificationEmail(body): 
    try:
        message = MIMEMultipart()
        message["From"] = 'your_email@example.com'
        message["To"] = 'recipient_email@example.com'
        message["Subject"] = "Error OpenDCIM"
        message.attach(MIMEText(body, "plain"))
        with smtplib.SMTP(host="mail.example.com", port=25) as server:
            server.starttls()
            server.sendmail('your_email@example.com', 'recipient_email@example.com', message.as_string())
    except Exception as e:
        print(f"Error sending email: {e}")
