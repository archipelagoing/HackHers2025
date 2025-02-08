#4:42p archisa 
import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

private_key = os.getenv("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n')


# Create credentials dictionary from environment variables
cred_dict = {
    "type": "service_account",
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key": private_key,
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "token_uri": "https://oauth2.googleapis.com/token", #Required for Firestore authentication

}

# Initialize Firebase with credentials from environment variables
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)

# Firestore database instance
db = firestore.client()
