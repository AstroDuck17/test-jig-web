from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .routes import router

app = FastAPI()
app.include_router(router)

# Mount static files if not already mounted
app.mount("/static", StaticFiles(directory="fastapi_app/static"), name="static")


# Serve favicon.ico
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("fastapi_app/static/favicon.ico")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fastapi_app.main:app", host="0.0.0.0", port=8000, reload=True)