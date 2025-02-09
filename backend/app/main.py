from fastapi import FastAPI
from app.routes import auth

app = FastAPI()

# Register routes
app.include_router(auth.router)

@app.get("/")
def home():
    return {"message": "Welcome to FastAPI"}
