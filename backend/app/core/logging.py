import logging
import sys
from app.core.config import settings

def setup_logging() -> None:
    log_level = logging.INFO
    if settings.APP_ENV == "development":
        log_level = logging.DEBUG
        
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set levels for third party logs if necessary
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
logger = logging.getLogger("ai_review_platform")
