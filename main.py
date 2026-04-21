from fastapi import FastAPI
from pedidos.routes import router

app = FastAPI(title="API de Pedidos", version="1.0.0")
app.include_router(router)
