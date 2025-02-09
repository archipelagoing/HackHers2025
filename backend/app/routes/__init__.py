# Import all routes to make them available
from .auth import router as auth_router
from .users import router as users_router
from .match import router as match_router
# from .playlists import router as playlists_router  # Comment this if not using yet 