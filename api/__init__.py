from fastapi import FastAPI

from api import authentication, user_settings

router = FastAPI(docs_url="/docs")
router.include_router(authentication.router)
router.include_router(user_settings.router)
