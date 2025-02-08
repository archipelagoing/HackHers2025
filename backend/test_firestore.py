from app.database import db

def test_firestore():
    test_ref = db.collection("test").document("connection_check")
    test_ref.set({"message": "Firestore is connected!"})

    doc = test_ref.get()
    if doc.exists:
        print("✅ Firestore Connection Successful:", doc.to_dict())
    else:
        print("❌ Firestore Connection Failed!")

test_firestore()
