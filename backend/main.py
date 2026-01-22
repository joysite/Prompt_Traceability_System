from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.models import Base, engine
from backend.routers import auth, batch_admin, trace


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Agri Traceability QR System (MVP)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(batch_admin.router)
app.include_router(trace.router)
