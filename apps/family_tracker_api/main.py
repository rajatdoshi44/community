from fastapi import FastAPI
from apps.family_tracker_api.router import router as family_tracker_router

app = FastAPI(title="family-tracker-api", version="0.1.0")
app.include_router(family_tracker_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8007)
