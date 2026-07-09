from fastapi import FastAPI

app = FastAPI(
    title="CodeAtlas Analysis Engine",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "service": "analysis-engine",
        "status": "running"
    }