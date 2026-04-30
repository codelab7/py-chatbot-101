from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import mysql.connector
import bcrypt
import jwt
import os

app = FastAPI(title="Auth API", description="Register, Login & JWT Token API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

SECRET_KEY = "108!@#$%^&Asut"
ALGORITHM  = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 90

DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "108@#$",
    "database": "auth_db",
}

# ─────────────────────────────────────────────
#  Default Bot Responses
# ─────────────────────────────────────────────
DEFAULT_RESPONSES = {
    "hi": "Hello! How can I help you today? 😊",
    "hello": "Hey there! What can I do for you? 👋",
    "how are you": "I'm doing great! Thanks for asking. How about you? 😄"
    
}

DEFAULT_FALLBACK = "That's an interesting question! I'm still learning. Can you ask me something else? 🤔"

def get_bot_response(message: str) -> str:
    msg = message.lower().strip()
    # Exact match
    if msg in DEFAULT_RESPONSES:
        return DEFAULT_RESPONSES[msg]
    # Partial match
    for key, response in DEFAULT_RESPONSES.items():
        if key in msg:
            return response
    return DEFAULT_FALLBACK

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

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         INT AUTO_INCREMENT PRIMARY KEY,
            name       VARCHAR(100)        NOT NULL,
            email      VARCHAR(150) UNIQUE NOT NULL,
            password   VARCHAR(255)        NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id         INT AUTO_INCREMENT PRIMARY KEY,
            user_id    INT          NOT NULL,
            title      VARCHAR(255) DEFAULT 'New Chat',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id         INT AUTO_INCREMENT PRIMARY KEY,
            chat_id    INT          NOT NULL,
            user_id    INT          NOT NULL,
            role       VARCHAR(10)  NOT NULL,
            message    TEXT         NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chat_id) REFERENCES chats(id),
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

class CreateChatRequest(BaseModel):
    title: str = "New Chat"

class SendMessageRequest(BaseModel):
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
#  Routes
# ─────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "Auth API is running 🚀"}

# ── REGISTER ──
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

    # Register થતાં જ નવો Chat automatically બનાવો
    cur.execute("INSERT INTO chats (user_id, title) VALUES (%s, %s)", (user_id, "My First Chat"))
    db.commit()
    chat_id = cur.lastrowid

    # Default welcome message save કરો
    welcome = "Welcome! I'm AstraBot 🤖 Ask me anything!"
    cur.execute(
        "INSERT INTO messages (chat_id, user_id, role, message) VALUES (%s, %s, %s, %s)",
        (chat_id, user_id, "bot", welcome)
    )
    db.commit()

    token = create_access_token({"sub": str(user_id), "email": body.email})

    return {
        "message": "User registered successfully",
        "user": {"id": user_id, "name": body.name, "email": body.email},
        "chat": {"id": chat_id, "title": "My First Chat"},
        "bot_welcome": welcome,
        "access_token": token,
        "token_type": "bearer",
    }

# ── LOGIN ──
@app.post("/api/login")
def login(body: LoginRequest, db=Depends(get_db)):
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE email = %s", (body.email,))
    user = cur.fetchone()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not bcrypt.checkpw(body.password.encode(), user["password"].encode()):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Login થતાં જ user નો પહેલો chat fetch કરો
    cur.execute("SELECT id, title FROM chats WHERE user_id = %s ORDER BY created_at ASC LIMIT 1", (user["id"],))
    chat = cur.fetchone()

    token = create_access_token({"sub": str(user["id"]), "email": user["email"]})

    return {
        "message": "Login successful",
        "user": {"id": user["id"], "name": user["name"], "email": user["email"]},
        "chat": chat,
        "access_token": token,
        "token_type": "bearer",
    }

# ── ME ──
@app.get("/api/me")
def get_me(credentials: HTTPAuthorizationCredentials = Depends(security), db=Depends(get_db)):
    payload = verify_token(credentials.credentials)
    user_id = payload.get("sub")
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT id, name, email, created_at FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user}

# ─────────────────────────────────────────────
#  Chat APIs
# ─────────────────────────────────────────────
@app.post("/api/chats", status_code=status.HTTP_201_CREATED)
def create_chat(body: CreateChatRequest, current_user=Depends(get_current_user), db=Depends(get_db)):
    user_id = int(current_user["sub"])
    cur = db.cursor(dictionary=True)
    cur.execute("INSERT INTO chats (user_id, title) VALUES (%s, %s)", (user_id, body.title))
    db.commit()
    chat_id = cur.lastrowid
    return {
        "message": "Chat created successfully",
        "chat": {"id": chat_id, "title": body.title, "user_id": user_id}
    }

@app.get("/api/chats")
def get_chats(current_user=Depends(get_current_user), db=Depends(get_db)):
    user_id = int(current_user["sub"])
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT c.id, c.title, c.created_at, COUNT(m.id) as message_count
        FROM chats c
        LEFT JOIN messages m ON c.id = m.chat_id
        WHERE c.user_id = %s
        GROUP BY c.id
        ORDER BY c.created_at DESC
    """, (user_id,))
    return {"chats": cur.fetchall()}

@app.get("/api/chats/{chat_id}")
def get_chat(chat_id: int, current_user=Depends(get_current_user), db=Depends(get_db)):
    user_id = int(current_user["sub"])
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM chats WHERE id = %s AND user_id = %s", (chat_id, user_id))
    chat = cur.fetchone()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return {"chat": chat}

@app.delete("/api/chats/{chat_id}")
def delete_chat(chat_id: int, current_user=Depends(get_current_user), db=Depends(get_db)):
    user_id = int(current_user["sub"])
    cur = db.cursor()
    cur.execute("SELECT id FROM chats WHERE id = %s AND user_id = %s", (chat_id, user_id))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Chat not found")
    cur.execute("DELETE FROM messages WHERE chat_id = %s", (chat_id,))
    cur.execute("DELETE FROM chats WHERE id = %s", (chat_id,))
    db.commit()
    return {"message": "Chat deleted successfully"}

# ─────────────────────────────────────────────
#  Message APIs
# ─────────────────────────────────────────────

# ── Message મોકલો + Bot નો Reply ──
@app.post("/api/chats/{chat_id}/messages", status_code=status.HTTP_201_CREATED)
def send_message(chat_id: int, body: SendMessageRequest, current_user=Depends(get_current_user), db=Depends(get_db)):
    user_id = int(current_user["sub"])
    cur = db.cursor(dictionary=True)

    # Chat exist?
    cur.execute("SELECT id FROM chats WHERE id = %s AND user_id = %s", (chat_id, user_id))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Chat not found")

    # User message save
    cur.execute(
        "INSERT INTO messages (chat_id, user_id, role, message) VALUES (%s, %s, %s, %s)",
        (chat_id, user_id, "user", body.message)
    )
    db.commit()
    user_message_id = cur.lastrowid

    # Bot response generate
    bot_reply = get_bot_response(body.message)

    # Bot message save
    cur.execute(
        "INSERT INTO messages (chat_id, user_id, role, message) VALUES (%s, %s, %s, %s)",
        (chat_id, user_id, "bot", bot_reply)
    )
    db.commit()
    bot_message_id = cur.lastrowid

    return {
        "message": "Message sent successfully",
        "user_message": {
            "message_id": user_message_id,
            "chat_id": chat_id,
            "role": "user",
            "message": body.message,
        },
        "bot_response": {
            "message_id": bot_message_id,
            "chat_id": chat_id,
            "role": "bot",
            "message": bot_reply,
        }
    }

@app.get("/api/chats/{chat_id}/messages")
def get_messages(chat_id: int, current_user=Depends(get_current_user), db=Depends(get_db)):
    user_id = int(current_user["sub"])
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT id FROM chats WHERE id = %s AND user_id = %s", (chat_id, user_id))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Chat not found")
    cur.execute("""
        SELECT id as message_id, chat_id, role, message, created_at
        FROM messages WHERE chat_id = %s ORDER BY created_at ASC
    """, (chat_id,))
    messages = cur.fetchall()
    return {"chat_id": chat_id, "total_messages": len(messages), "messages": messages}

@app.delete("/api/chats/{chat_id}/messages/{message_id}")
def delete_message(chat_id: int, message_id: int, current_user=Depends(get_current_user), db=Depends(get_db)):
    user_id = int(current_user["sub"])
    cur = db.cursor()
    cur.execute(
        "SELECT id FROM messages WHERE id = %s AND chat_id = %s AND user_id = %s",
        (message_id, chat_id, user_id)
    )
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Message not found")
    cur.execute("DELETE FROM messages WHERE id = %s", (message_id,))
    db.commit()
    return {"message": f"Message {message_id} deleted successfully"}
