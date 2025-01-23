import os
from twilio.rest import Client
import smtplib

# Using a .env file to retrieve the phone numbers and tokens.


class NotificationManager:

    def __init__(self):
        self.smtp_address = os.environ["EMAIL_PROVIDER_SMTP_ADDRESS"]
        self.email = os.environ["MY_EMAIL"]
        self.email_password = os.environ["MY_EMAIL_PASSWORD"]
        self.twilio_virtual_number = os.environ["TWILIO_VIRTUAL_NUMBER"]
        self.twilio_verified_number = os.environ["TWILIO_VERIFIED_NUMBER"]
        self.whatsapp_number = os.environ["TWILIO_WHATSAPP_NUMBER"]
        self.client = Client(os.environ['TWILIO_SID'], os.environ["TWILIO_AUTH_TOKEN"])
        self.connection = smtplib.SMTP(host=os.environ["EMAIL_PROVIDER_SMTP_ADDRESS"], port=587)

    def send_sms(self, message_body):
        """
        Sends an SMS message through the Twilio API
        
            >>> Function takes a message body as input 
            >>> Uses Twilio API to send an SMS from virtual number (provided by Twilio) to your own "verified" number
            >>> It logs the unique SID (Session ID) of the message
            >>> This can be used to verify that message was sent successfully

        Parameters:
            message_body (str): The text content of the SMS message to be sent.

        Returns:
            None
        
            >>> Twilio client (`self.client`) should be initialized 
            >>> Then authenticated with Twilio account credentials prior to using this function 
            >>> Ideally this occurs when the 'Notification Manager' gets initialized
        """
        message = self.client.messages.create(
            from_=self.twilio_virtual_number,
            body=message_body,
            to=self.twilio_verified_number
        )
        # Prints if successfully sent.
        print(message.sid)

    # Is SMS not working, or prefer whatsapp? Connect to the WhatsApp Sandbox...
    # https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
    def send_whatsapp(self, message_body):
        message = self.client.messages.create(
            from_=f'whatsapp:{self.whatsapp_number}',
            body=message_body,
            to=f'whatsapp:{self.twilio_verified_number}'
        )
        print(message.sid)

    # Function to send emails to all individuals with an email in the 'users' Google Sheet
    def send_emails(self, email_list, email_body):

        try:
            with self.connection as connection:
                connection.starttls()
                connection.login(user=self.email, password=self.email_password)

                for email in email_list:
                    connection.sendmail(
                        from_addr=self.email,
                        to_addrs=email,
                        msg=f"Subject:New Low Price Flight!\n\n{email_body}".encode('utf-8')
                    )

        except Exception as e:
            print(f"An error occurred: {e}")
