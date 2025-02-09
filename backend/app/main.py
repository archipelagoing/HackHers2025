from fastapi import FastAPI
from .routes import auth, users, match, ai_claude  # Remove playlists if not using yet

app = FastAPI()

# Include all routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(match.router, prefix="/match", tags=["match"])
app.include_router(ai_claude.router, prefix="/ai", tags=["ai"])
# app.include_router(playlists.router, prefix="/playlists", tags=["playlists"])  # Comment if not using

@app.get("/")
def home():
    return {"message": "Welcome to FastAPI"}
