from fastapi import FastAPI

description = """
New reshape backend server coding challenge

## Items

- You can **zoom image**.
- Compute **cosine similarity between images**
- 
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


# Add some middlewares here if you want....

@app.get("/health")
async def health_check():
    return {"status": "200 Ok"}