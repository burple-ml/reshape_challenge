''' main app code '''
from fastapi import FastAPI
from .images.routes import router

description = """
New reshape backend server coding challenge

## Items

- You can provide an image here and get a **cropped version of it**.
- Compute the **cosine similarity** between provided images.
- Compute a hash of the base64 binary provided image
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

# health check for health monitoring
@app.get("/health", include_in_schema=False)
async def health_check():
    return {"status": "200 OK"}