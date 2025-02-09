#4:42p archisa 
import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# 1. Load environment variables from .env
load_dotenv()

# 2. Set up Firebase credentials using your .env variables
cred_dict = {
    "type": "service_account",
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "token_uri": "https://oauth2.googleapis.com/token",
}

# 3. Initialize Firebase with these credentials
try:
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
except ValueError as e:
    print("Firebase Credential Error:", e)
    print("Check your .env file and make sure FIREBASE_PRIVATE_KEY is correct")
    raise
# 4. Create a database instance that other files use
db = firestore.client()

def get_db():
    """Returns the Firestore database instance."""
    return db



