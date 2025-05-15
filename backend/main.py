from fastapi import FastAPI
from api import auth, face
from api import live_monitor

app = FastAPI()
app.include_router(auth.router)
app.include_router(face.router)
app.include_router(live_monitor.router)

@app.get("/health/")
def health_check():
    return {"status": "OK"}
