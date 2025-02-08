#4:37p archisa 
import firebase_admin
from firebase_admin import credentials, firestore

# Load Firebase credentials
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# Firestore database instance
db = firestore.client()
