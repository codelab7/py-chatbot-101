from fastapi import FastAPI

app = FastAPI()

@app.get("/chat")
def chat(text: str):
    if text.lower() == "user":
        return {"response": "Astha"}
    return {"response": "unknown"}
