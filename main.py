from fastapi import FastAPI
from routes.auth import router as auth_router
from routes.agent import router as agent_router


app = FastAPI(title="AI Agent API")

app.include_router(auth_router)
app.include_router(agent_router)

@app.get("/health")
async def health():
    return {"status":"ok"}
