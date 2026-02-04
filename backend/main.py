from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    """Endpoint raiz - health check."""
    return {
        "status": "online",
        "service": "LaudoSync API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
