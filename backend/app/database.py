#4:42p archisa 
import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Load Firebase credentials
load_dotenv()
cred = credentials.Certificate(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
firebase_admin.initialize_app(cred)

# Firestore database instance
db = firestore.client()
