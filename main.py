from fastapi import FastAPI
from routes.auth import router as auth_router
from routes.agent import router as agent_router
from routes.agent_v2 import router as agent_v2_router
from routes.ws_v2 import router as ws_v2_router

app = FastAPI(title="AI Agent API")

app.include_router(auth_router)
app.include_router(agent_router)
app.include_router(agent_v2_router)
app.include_router(ws_v2_router)


@app.get("/health")
async def health():
    return {"status":"ok"}
