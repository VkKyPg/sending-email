from google.appengine.api import mail

def send_invitation(origin, recipient, messageX, attachemntsX):
    message = mail.EmailMessage()
    message.sender = origin
    message.to = recipient
    message.body = messageX
    message.attachments = attachemntsX
    message.send()
