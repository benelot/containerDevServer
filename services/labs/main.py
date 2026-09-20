from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(docs_url=None, redoc_url=None)
app.mount("/", StaticFiles(directory="public", html=True), name="site")
