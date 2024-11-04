from fastapi.middleware.cors import CORSMiddleware

from SERVER.START import app

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # или укажите конкретные URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
