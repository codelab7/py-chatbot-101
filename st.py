from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta,timezone
import json
import mysql.connector
import bcrypt
import jwt
import httpx

app = FastAPI(title="Auth API", description="Register, Login & JWT Token API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

SECRET_KEY = "108!@#$%^&Asuttariya_Astha"
ALGORITHM  = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 90

OLLAMA_URL   = "http://localhost:11434/api/chat"    
OLLAMA_MODEL = "gemma:2b"

DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "108@#$",
    "database": "auth_db",
}

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are AstraBot, an expert AI coding assistant.\n\n"
        "You help with:\n"
        "- Python\n- FastAPI\n- React\n- HTML/CSS/JS\n"
        "- MySQL\n- JWT Authentication\n- APIs\n"
        "- Web development\n- AI chatbots\n\n"
        "Always give detailed and correct coding answers\n"
          "Rules:\n"
        "1. Always answer in a structured format\n"
        "2. Start with a simple explanation\n"
        "3. Then give technical explanation\n"
        "4. Then provide examples (code if needed)\n"
        "5. Use bullet points when helpful\n"
        "6. Avoid unnecessary long text\n\n"

        "Special behavior:\n"
        "- If the user asks about FastAPI, give practical backend examples\n"
        "- If the user asks about errors, debug step-by-step\n"
        "- If the user asks 'why', explain concept clearly\n"
        "- If the user asks 'how', give steps\n\n"

        "Your goal is to behave like ChatGPT and help developers efficiently."

    )
}

# SYSTEM_PROMPT = {
#     "role": "system",
#     "content": "You are a fast coding assistant. Give clear and short answers with examples."
# }
# ─────────────────────────────────────────────
#  Database
# ─────────────────────────────────────────────
def get_connection():
    # ✅ FIX 5: database= parameter directly — USE statement નહીં
    return mysql.connector.connect(**DB_CONFIG)

def init_db():
    # ✅ FIX 5: પહેલા database વગર connect, create કરો, પછી database સાથે reconnect
    conn = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
    )
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}`")
    conn.commit()
    conn.close()

    # Reconnect with database selected
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()
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

try:
    init_db()
    print("✅ Database initialized")
except Exception as e:
    print(f"⚠️ DB init failed: {e} — check MySQL connection")

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
    expire  = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
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

def build_messages(history: list) -> list:
    messages = [SYSTEM_PROMPT]
    for h in history:
        messages.append({
            "role": "user" if h["role"] == "user" else "assistant",
            "content": h["message"]
        })
    return messages

# ─────────────────────────────────────────────
#  ✅ FIX 4: Non-stream AI — safe NDJSON parser
# ─────────────────────────────────────────────
async def get_ai_response(history: list) -> str:
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(300.0)) as client:
            response = await client.post(
                OLLAMA_URL,
                json={"model": OLLAMA_MODEL, "messages": build_messages(history), "stream": False}
            )
        if response.status_code != 200:
            return f"Ollama Error: {response.text}"

        # ✅ FIX 4: Safe parse — try single JSON first, fallback to NDJSON
        text = response.text.strip()
        try:
            data = json.loads(text)
            return data.get("message", {}).get("content", "AI response not found.")
        except json.JSONDecodeError:
            # Fallback: NDJSON line by line
            full = ""
            for line in text.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                    full += chunk.get("message", {}).get("content", "")
                    if chunk.get("done"):
                        break
                except json.JSONDecodeError:
                    continue
            return full or "AI response not found."

    except httpx.ReadTimeout:
        return "AI is taking too long to respond. Please try again."
    except Exception as e:
        import traceback; traceback.print_exc()
        return f"AI Error: {str(e)}"

# ─────────────────────────────────────────────
#  ✅ Stream generator
# ─────────────────────────────────────────────
async def stream_ai_response(history: list):
    received_any = False
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(connect=10.0, read=120.0, write=10.0,pool=10.0)) as client:
            async with client.stream(
                "POST",
                OLLAMA_URL,
                json={"model": OLLAMA_MODEL, "messages": build_messages(history), "stream": True,
        #                "options": {
        # "num_predict": 120,
        # "temperature": 0.3,
        # "top_k": 20,
        # "top_p": 0.9
                # }
                      },
            ) as response:

                if response.status_code != 200:
                    error_text = await response.aread()
                    yield f"\n[OLLAMA ERROR]: {error_text.decode()}"
                    return

              

                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        content = data.get("message", {}).get("content", "")
                        if content:
                            received_any = True
                            yield content
                        if data.get("done"):
                            break
                    except json.JSONDecodeError:
                        continue

        # ✅ FIX 1: received_any check OUTSIDE async with block
        if not received_any:
            yield "\n[WARNING]: No response from AI"

    except Exception as e:
        import traceback; traceback.print_exc()
        yield f"\n[ERROR]: {str(e)}"


# ─────────────────────────────────────────────
#  Routes
# ─────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "Chatbot is running 🚀"}

# ── REGISTER ──
@app.post("/api/register", status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT id FROM users WHERE email = %s", (body.email,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")
        hashed = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode()
        cur.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (body.name, body.email, hashed),
        )
        conn.commit()
        user_id = cur.lastrowid
        cur.execute("INSERT INTO chats (user_id, title) VALUES (%s, %s)", (user_id, "My First Chat"))
        conn.commit()
        chat_id = cur.lastrowid
        welcome = "Welcome! I'm AstraBot 🤖 Powered by LLaMA AI. Ask me anything!"
        cur.execute(
            "INSERT INTO messages (chat_id, user_id, role, message) VALUES (%s, %s, %s, %s)",
            (chat_id, user_id, "assistant", welcome)
        )
        conn.commit()
        token = create_access_token({"sub": str(user_id), "email": body.email})
        return {
            "message": "User registered successfully",
            "user": {"id": user_id, "name": body.name, "email": body.email},
            "chat": {"id": chat_id, "title": "My First Chat"},
            "ai_welcome": welcome,
            "access_token": token,
            "token_type": "bearer",
        }
    finally:
        conn.close()

# ── LOGIN ──
@app.post("/api/login")
def login(body: LoginRequest):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM users WHERE email = %s", (body.email,))
        user = cur.fetchone()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        if not bcrypt.checkpw(body.password.encode(), user["password"].encode()):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # ✅ FIX 6: chat None handle — empty list return
        cur.execute(
            "SELECT id, title FROM chats WHERE user_id = %s ORDER BY created_at ASC LIMIT 1",
            (user["id"],)
        )
        chat = cur.fetchone()  # None if no chats yet
        token = create_access_token({"sub": str(user["id"]), "email": user["email"]})
        return {
            "message": "Login successful",
            "user": {"id": user["id"], "name": user["name"], "email": user["email"]},
            "chat": chat or {},   # ✅ FIX 6: None ની જગ્યાએ empty dict
            "access_token": token,
            "token_type": "bearer",
        }
    finally:
        conn.close()

# ── ME ──
@app.get("/api/me")
def get_me(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = verify_token(credentials.credentials)
    user_id = payload.get("sub")
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:    
        cur.execute("SELECT id, name, email, created_at FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"user": user}
    finally:
        conn.close()

# ─────────────────────────────────────────────
#  Chat APIs
# ─────────────────────────────────────────────
@app.post("/api/chats", status_code=status.HTTP_201_CREATED)
def create_chat(body: CreateChatRequest, current_user=Depends(get_current_user)):
    user_id = int(current_user["sub"])
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("INSERT INTO chats (user_id, title) VALUES (%s, %s)", (user_id, body.title))
        conn.commit()
        chat_id = cur.lastrowid
        return {"message": "Chat created successfully", "chat": {"id": chat_id, "title": body.title, "user_id": user_id}}
    finally:
        conn.close()

@app.get("/api/chats")
def get_chats(current_user=Depends(get_current_user)):
    user_id = int(current_user["sub"])
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT c.id, c.title, c.created_at, COUNT(m.id) as message_count
            FROM chats c LEFT JOIN messages m ON c.id = m.chat_id
            WHERE c.user_id = %s GROUP BY c.id ORDER BY c.created_at DESC
        """, (user_id,))
        return {"chats": cur.fetchall()}
    finally:
        conn.close()

@app.get("/api/chats/{chat_id}")
def get_chat(chat_id: int, current_user=Depends(get_current_user)):
    user_id = int(current_user["sub"])
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM chats WHERE id = %s AND user_id = %s", (chat_id, user_id))
        chat = cur.fetchone()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        return {"chat": chat}
    finally:
        conn.close()

@app.delete("/api/chats/{chat_id}")
def delete_chat(chat_id: int, current_user=Depends(get_current_user)):
    user_id = int(current_user["sub"])
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM chats WHERE id = %s AND user_id = %s", (chat_id, user_id))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Chat not found")
        cur.execute("DELETE FROM messages WHERE chat_id = %s", (chat_id,))
        cur.execute("DELETE FROM chats WHERE id = %s", (chat_id,))
        conn.commit()
        return {"message": "Chat deleted successfully"}
    finally:
        conn.close()

# ─────────────────────────────────────────────
#  Message APIs
# ─────────────────────────────────────────────

# ✅ /stream MUST be BEFORE /{chat_id}/messages — route order
@app.post("/api/chats/{chat_id}/messages/stream")
async def send_message_stream(
    chat_id: int,
    body: SendMessageRequest,
    current_user=Depends(get_current_user)
):
    user_id = int(current_user["sub"])

    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT id FROM chats WHERE id = %s AND user_id = %s", (chat_id, user_id))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Chat not found")

        # History BEFORE saving user message
        cur.execute("""
            SELECT role, message FROM messages
            WHERE chat_id = %s ORDER BY created_at ASC LIMIT 20
        """, (chat_id,))
        history = [{"role": r["role"], "message": r["message"]} for r in cur.fetchall()]

        # Save user message to DB
        cur.execute(
            "INSERT INTO messages (chat_id, user_id, role, message) VALUES (%s, %s, %s, %s)",
            (chat_id, user_id, "user", body.message)
        )
        conn.commit()

        # Add to history for AI
        history.append({"role": "user", "message": body.message})

    finally:
        conn.close()  # Close BEFORE generator starts

    # ── Stream Generator ──
    async def generator():
        full_response = ""
        try:
            async for chunk in stream_ai_response(history):
                full_response += chunk
                yield chunk
        except Exception as e:
            yield f"\n[GENERATOR ERROR]: {str(e)}"
            return

        # ✅ FIX 2: New connection inside generator
        if full_response:
            save_conn = get_connection()
            save_cur = save_conn.cursor()
            try:
                save_cur.execute(
                    "INSERT INTO messages (chat_id, user_id, role, message) VALUES (%s, %s, %s, %s)",
                    (chat_id, user_id, "assistant", full_response)
                )
                save_conn.commit()
            except Exception as db_err:
                print(f"DB save error: {db_err}")
            finally:
                save_conn.close()

    return StreamingResponse(
        generator(),
        media_type="text/plain",
        headers={
            "X-Accel-Buffering": "no",
            "Cache-Control": "no-cache",
        }
    )


# ── Non-stream JSON endpoint ──
@app.post("/api/chats/{chat_id}/messages", status_code=status.HTTP_201_CREATED)
async def send_message(
    chat_id: int,
    body: SendMessageRequest,
    current_user=Depends(get_current_user)
):
    user_id = int(current_user["sub"])
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT id FROM chats WHERE id = %s AND user_id = %s", (chat_id, user_id))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Chat not found")

        # History BEFORE saving
        cur.execute("""
            SELECT role, message FROM messages
            WHERE chat_id = %s ORDER BY created_at ASC LIMIT 20
        """, (chat_id,))
        history = [{"role": r["role"], "message": r["message"]} for r in cur.fetchall()]

        # Save user message
        cur.execute(
            "INSERT INTO messages (chat_id, user_id, role, message) VALUES (%s, %s, %s, %s)",
            (chat_id, user_id, "user", body.message)
        )
        conn.commit()
        user_message_id = cur.lastrowid

        # Add to history
        history.append({"role": "user", "message": body.message})

        # Get AI response (non-stream)
        ai_reply = await get_ai_response(history)

        cur.execute(
            "INSERT INTO messages (chat_id, user_id, role, message) VALUES (%s, %s, %s, %s)",
            (chat_id, user_id, "assistant", ai_reply)
        )
        conn.commit()
        ai_message_id = cur.lastrowid

        return {
            "message": "Message sent successfully",
            "user_message": {
                "message_id": user_message_id,
                "chat_id": chat_id,
                "role": "user",
                "message": body.message,
            },
            "ai_response": {
                "message_id": ai_message_id,
                "chat_id": chat_id,
                "role": "assistant",
                "message": ai_reply,
            }
        }
    finally:
        conn.close()


@app.get("/api/chats/{chat_id}/messages")
def get_messages(chat_id: int, current_user=Depends(get_current_user)):
    user_id = int(current_user["sub"])
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT id FROM chats WHERE id = %s AND user_id = %s", (chat_id, user_id))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Chat not found")
        cur.execute("""
            SELECT id as message_id, chat_id, role, message, created_at
            FROM messages WHERE chat_id = %s ORDER BY created_at ASC
        """, (chat_id,))
        messages = cur.fetchall()
        return {"chat_id": chat_id, "total_messages": len(messages), "messages": messages}
    finally:
        conn.close()


@app.delete("/api/chats/{chat_id}/messages/{message_id}")
def delete_message(chat_id: int, message_id: int, current_user=Depends(get_current_user)):
    user_id = int(current_user["sub"])
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id FROM messages WHERE id = %s AND chat_id = %s AND user_id = %s",
            (message_id, chat_id, user_id)
        )
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Message not found")
        cur.execute("DELETE FROM messages WHERE id = %s", (message_id,))
        conn.commit()
        return {"message": f"Message {message_id} deleted successfully"}
    finally:
        conn.close()