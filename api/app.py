from fastapi import FastAPI
import uvicorn
from api import router as api_router
from common.settings import settings

app = FastAPI(docs_url='/')

app.include_router(api_router)

if __name__ == '__main__':  # pragma: no cover
    uvicorn.run(
        "app:app",
        host='localhost',
        port=settings.PORT,
    )
