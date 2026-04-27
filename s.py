from fastapi import FastAPI, APIRouter
from pydantic import BaseModel

app = FastAPI()
router = APIRouter()

class Msg(BaseModel):
    text: str

@router.post("/chat")
def chat(msg: Msg):
    if msg.text.lower() == "user":
        return {"response": "Aastha"}
    return {"response": "type user"}


app.include_router(router)
