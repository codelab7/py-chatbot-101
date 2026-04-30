from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import mysql.connector
import bcrypt
import jwt
import httpx
import os

# ─────────────────────────────────────────────
#  Config
# ─────────────────────────────────────────────
SECRET_KEY = "108!@#$%^&Asut"
ALGORITHM  = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

GEMINI_API_KEY = "AIzaSyCEmdgQd6FgAgQEbNZi1gNg1NI2t77ukYU"   # ← અહીં તમારી Gemini API Key નાખો
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "108@#$",
    "database": "chatbot_db",
}

# ─────────────────────────────────────────────
#  App Setup
# ─────────────────────────────────────────────
app = FastAPI(title="Chatbot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# ─────────────────────────────────────────────
#  Database
# ─────────────────────────────────────────────
def get_db():
    conn = mysql.connector.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    conn = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
    )
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
    cur.execute(f"USE {DB_CONFIG['database']}")

    # Users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         INT AUTO_INCREMENT PRIMARY KEY,
            name       VARCHAR(100)        NOT NULL,
            email      VARCHAR(150) UNIQUE NOT NULL,
            password   VARCHAR(255)        NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Chat history table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id         INT AUTO_INCREMENT PRIMARY KEY,
            user_id    INT          NOT NULL,
            role       VARCHAR(10)  NOT NULL,
            message    TEXT         NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ─────────────────────────────────────────────
#  Schemas
# ─────────────────────────────────────────────
class RegisterRequest(BaseModel):
    name:     str
    email:    EmailStr
    password: str

class LoginRequest(BaseModel):
    email:    EmailStr
    password: str

class ChatRequest(BaseModel):
    message: str

# ─────────────────────────────────────────────
#  JWT Helpers
# ─────────────────────────────────────────────
def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire  = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expire})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return verify_token(credentials.credentials)

# ─────────────────────────────────────────────
#  Auth Routes
# ─────────────────────────────────────────────
@app.get("/")
def root():
    return FileResponse("static/index.html")

@app.post("/api/register", status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, db=Depends(get_db)):
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT id FROM users WHERE email = %s", (body.email,))
    if cur.fetchone():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode()
    cur.execute(
        "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
        (body.name, body.email, hashed),
    )
    db.commit()
    user_id = cur.lastrowid
    token = create_access_token({"sub": str(user_id), "email": body.email, "name": body.name})

    return {
        "message": "User registered successfully",
        "user": {"id": user_id, "name": body.name, "email": body.email},
        "access_token": token,
        "token_type": "bearer",
    }

@app.post("/api/login")
def login(body: LoginRequest, db=Depends(get_db)):
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE email = %s", (body.email,))
    user = cur.fetchone()

    if not user or not bcrypt.checkpw(body.password.encode(), user["password"].encode()):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(user["id"]), "email": user["email"], "name": user["name"]})

    return {
        "message": "Login successful",
        "user": {"id": user["id"], "name": user["name"], "email": user["email"]},
        "access_token": token,
        "token_type": "bearer",
    }

# ─────────────────────────────────────────────
#  Chat Routes
# ─────────────────────────────────────────────
@app.post("/api/chat")
async def chat(body: ChatRequest, current_user=Depends(get_current_user), db=Depends(get_db)):
    user_id = int(current_user["sub"])
    user_message = body.message

    cur = db.cursor(dictionary=True)

    # Last 10 messages history fetch કરો
    cur.execute("""
        SELECT role, message FROM chat_history
        WHERE user_id = %s
        ORDER BY created_at DESC LIMIT 10
    """, (user_id,))
    history = list(reversed(cur.fetchall()))

    # Gemini format માં history બનાવો
    contents = []
    for h in history:
        contents.append({
            "role": "user" if h["role"] == "user" else "model",
            "parts": [{"text": h["message"]}]
        })

    # નવો message add કરો
    contents.append({"role": "user", "parts": [{"text": user_message}]})

    # Gemini API call
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GEMINI_URL,
            json={"contents": contents},
            timeout=30,
        )

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="AI API error")

    ai_reply = response.json()["candidates"][0]["content"]["parts"][0]["text"]

    # Chat history save કરો
    cur.execute(
        "INSERT INTO chat_history (user_id, role, message) VALUES (%s, %s, %s)",
        (user_id, "user", user_message)
    )
    cur.execute(
        "INSERT INTO chat_history (user_id, role, message) VALUES (%s, %s, %s)",
        (user_id, "assistant", ai_reply)
    )
    db.commit()

    return {"reply": ai_reply}


@app.get("/api/chat/history")
def get_history(current_user=Depends(get_current_user), db=Depends(get_db)):
    user_id = int(current_user["sub"])
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT role, message, created_at FROM chat_history
        WHERE user_id = %s ORDER BY created_at ASC
    """, (user_id,))
    return {"history": cur.fetchall()}


@app.delete("/api/chat/history")
def clear_history(current_user=Depends(get_current_user), db=Depends(get_db)):
    user_id = int(current_user["sub"])
    cur = db.cursor()
    cur.execute("DELETE FROM chat_history WHERE user_id = %s", (user_id,))
    db.commit()
    return {"message": "Chat history cleared"}
