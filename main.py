import requests
import random
import string
import time

def get_random_domain():
    response = requests.get("https://api.mail.tm/domains")
    data = response.json()
    return data["hydra:member"][0]["domain"]

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def register_email(email, password):
    url = "https://api.mail.tm/accounts"
    payload = {
        "address": email,
        "password": password
    }
    response = requests.post(url, json=payload)
    if response.status_code == 201:
        print("Email registered successfully!")
    elif response.status_code == 422:
        print("Email already exists, trying to generate a new one...")
    else:
        print(f"Failed to register email: {response.status_code} - {response.text}")

def get_token(email, password):
    url = "https://api.mail.tm/token"
    payload = {
        "address": email,
        "password": password
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()["token"]
    else:
        print(f"Failed to get token: {response.status_code} - {response.text}")
        return None
    
def check_inbox(token):
    url = "https://api.mail.tm/messages"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    data = response.json()

    messages = data.get("hydra:member", [])

    if not messages:
        print("No messages found in inbox.")
        return None
    
    print(f"Found {len(messages)} messages in inbox.")
    for message in messages:
        print(f"From: {message['from']['address']}")
        print(f"Subject: {message['subject']}")
        print(f"Date: {message['createdAt']}")
        print(f"ID: {message['id']}")
        print("-----------------------")

    return messages

def wait_for_messages(token, timeout=60, interval=5):
    print(f"Waiting for new messages (timeout: {timeout}s)...")
    start_time = time.time()

    while time.time() - start_time < timeout:
        messages = check_inbox(token)
        if messages:
            print("New messages found!")
            return messages
        else:
            time.sleep(interval)

    print("Timeout reached, no new messages found.")
    return None

def read_message(token, message_id):
    url = f"https://api.mail.tm/messages/{message_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200: 
        message = response.json()
        print(f"Message ID: {message['id']}")
        print(f"From: {message['from']['address']}")
        print(f"Subject: {message['subject']}")
        print(f"Date: {message['createdAt']}")
        print(f"Content: {message['text']}")
        with open(f"message_{message['from']['address']}_{message['id']}.txt", "w") as f:
            f.write(f"From: {message['from']['address']}\n")
            f.write(f"Subject: {message['subject']}\n")
            f.write(f"Date: {message['createdAt']}\n")
            f.write(f"Content: {message['text']}\n")
        print("Message saved to file.")
    else:
        print(f"Failed to read message: {response.status_code} - {response.text}")

def main():
    domain = get_random_domain()
    username = generate_random_string()
    password = generate_random_string(12)
    email = f"{username}@{domain}"

    print(f"Generated email: {email}")
    print(f"Generated password: {password}")

    register_email(email, password)
    token = get_token(email, password)

    if token:
        print(f"Token: {token}")
        messages = wait_for_messages(token, timeout=60, interval=5)
        if messages:
            read_message(token, messages[0]['id'])

    else:
            print("No messages found or failed to retrieve messages.")


if __name__ == "__main__":
    main()