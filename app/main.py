from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from . import models, database
from .routers import events
from .jobs import start_scheduler, shutdown_scheduler 


models.Base.metadata.create_all(bind=database.engine)
app = FastAPI(title="City Navigator")

@app.on_event("startup")
def _start():
    start_scheduler()  

@app.on_event("shutdown")
def _stop():
    shutdown_scheduler()  

app.include_router(events.router)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home_page():
    return FileResponse("static/index.html")

