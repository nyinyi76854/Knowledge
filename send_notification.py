import firebase_admin
from firebase_admin import credentials, messaging, db

# Initialize Firebase Admin SDK
cred = credentials.Certificate('serviceAccount.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://chatflow-59776-default-rtdb.firebaseio.com'
})

def get_fcm_token(receiver_email):
    """Fetch the FCM token for a given receiver email."""
    try:
        users_ref = db.reference('users')
        snapshot = users_ref.order_by_child('email').equal_to(receiver_email).get()
        for key, val in snapshot.items():
            fcm_token = val.get('fcmToken')
            print(f"FCM Token for {receiver_email}: {fcm_token}")
            return fcm_token
    except Exception as e:
        print(f"Error fetching FCM token: {str(e)}")
        return None

def send_notification(receiver_fcm_token, sender_name, text):
    """Send FCM notification to the receiver."""
    message = messaging.Message(
        notification=messaging.Notification(
            title='New Message',
            body=f"From: {sender_name}\n{text}",
        ),
        token=receiver_fcm_token,
        data={
            'senderName': sender_name,
            'message': text
        }
    )

    try:
        response = messaging.send(message)
        print('Successfully sent message:', response)
    except Exception as e:
        print(f"Error sending message: {str(e)}")

def load_user_name_for_email(sender_email):
    """Fetch the sender's name from the database based on the email."""
    try:
        names_ref = db.reference('names')
        snapshot = names_ref.order_by_child('email').equal_to(sender_email).get()
        last_timestamp = 0
        user_name = None

        for key, val in snapshot.items():
            timestamp = val.get('timestamp', 0)
            name = val.get('name', '').strip()
            if timestamp > last_timestamp and name:
                last_timestamp = timestamp
                user_name = name

        return user_name if user_name else sender_email  # Use email as fallback
    except Exception as e:
        print(f"Error fetching user name: {str(e)}")
        return sender_email  # Fallback to email in case of error

def process_message(message):
    """Process and send notification for a given message."""
    receiver_email = message.get('receiverEmail')
    sender_email = message.get('senderEmail')
    text = message.get('text', '')

    if receiver_email and sender_email:
        receiver_fcm_token = get_fcm_token(receiver_email)
        if receiver_fcm_token:
            sender_name = load_user_name_for_email(sender_email)
            send_notification(receiver_fcm_token, sender_name, text)
        else:
            print(f"No FCM token found for {receiver_email}")
    else:
        print(f"Invalid message data: {message}")

# Query for all unread messages and send notifications
def send_notifications_for_unread_messages():
    messages_ref = db.reference('messages')
    unread_messages = messages_ref.order_by_child('isRead').equal_to(False).get()

    for key, message in unread_messages.items():
        print(f"Processing unread message: {message}")
        process_message(message)

# Monitoring the Firebase Realtime Database for new messages
def monitor_new_messages():
    messages_ref = db.reference('messages')
    print("Monitoring new messages for notifications... (Type '->' to exit)")

    def message_handler(event):
        message = event.data
        if message and not message.get('isRead', True):
            print(f"New unread message detected: {message}")
            process_message(message)

    messages_ref.listen(message_handler)

if __name__ == "__main__":
    # First, send notifications for all unread messages
    send_notifications_for_unread_messages()

    # Then, monitor for new messages in real-time
    monitor_new_messages()
