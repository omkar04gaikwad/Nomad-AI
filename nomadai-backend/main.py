import uvicorn
from src.api.routes.form import app

if __name__ == "__main__":
    uvicorn.run(
        "src.api.routes.form:app",
        port=8000,
        reload=True,
        log_level="info"
    )
