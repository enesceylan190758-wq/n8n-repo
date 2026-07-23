from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from routers import health, mcp, ai, webhooks

app = FastAPI(
    title="Nefalix MCP Server",
    description="GEO/AEO teknik denetim, AI skorlama ve board-ready özet motoru",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://nefalixai.com", "https://dashboard.nefalixai.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(mcp.router)
app.include_router(ai.router)
app.include_router(webhooks.router)


@app.get("/")
async def root():
    return {
        "service": "Nefalix MCP Server",
        "version": "0.1.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "mcp_context": "/mcp/context/{clinic_id}",
            "audit": "/ai/audit",
            "score": "/ai/score",
            "summary": "/ai/summary",
            "correlate": "/ai/correlate",
            "executive": "/ai/executive/{clinic_id}",
            "upload_enps": "/ai/upload/enps",
            "n8n_webhook": "/webhooks/n8n",
        },
    }
