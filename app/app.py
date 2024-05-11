''' main app code '''
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from .images.routes import router
import os

base_path = "./app"

description = """
New reshape backend server coding challenge

## Items

- You can provide an image here and get a **cropped version of it**.
- Compute the **cosine similarity** between provided images.
- Compute a hash of the provided image. 

all images must be provided as form data in binary format. remember that when you are building the frontend for this application.
"""

app = FastAPI(
    title="Not a real server",
    description=description,
    summary="Challenge for reshape interview",
    version="0.0.1",
    terms_of_service="https://thesecatsdonotexist.com/",
    contact={
        "name": "Raghav",
        "url": "http://www.raghav.dk",
        "email": "raghav@beskedboks.dk",
    },
    license_info={
        "name": "Not Apache 2.0",
        "url": "https://thesecatsdonotexist.com/",
    },
)


# Add some middlewares here as per need..... 

# Include routes from user router
app.include_router(router, prefix="/image", tags=["imageOps"])

# Mount the "static" directory to the "/static" route
app.mount("/static", StaticFiles(directory=os.path.join(base_path, "static")), name="static")

# Serve index.html explicitly from the root route ("/")
@app.get("/")
async def read_index():
    return FileResponse(os.path.join(base_path, "static", "views", "index.html"))

# health check for health monitoring
@app.get("/health", include_in_schema=False)
async def health_check():
    return {"status": "200 OK"}