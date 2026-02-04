from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path

from app.routers import audits

# Cria a aplicação FastAPI
app = FastAPI(
    title="LaudoSync API",
    description="API para comparação automatizada de laudos médicos",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração de CORS (permite requisições do frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra os routers
app.include_router(audits.router)


@app.get("/")
async def root():
    """Serve o frontend HTML."""
    html_path = Path(__file__).parent / "static" / "index.html"
    return FileResponse(html_path, media_type="text/html")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
