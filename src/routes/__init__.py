from .users import router as user_router
from .oauth_auth import router as google_auth_router
routers = [
    user_router,
    google_auth_router,
]
