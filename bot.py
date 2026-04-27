from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Msg(BaseModel):
    text: str

@app.post("/chat")
def chat(msg: Msg):
    if msg.text.lower() == "ping":
        return {"response": "pong"}
    else:
        return {"response": "please type ping"}
#hello