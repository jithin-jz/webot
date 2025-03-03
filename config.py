import os
import redis
import logging
from datetime import timedelta

class Config:
    """Base configuration class."""
    
    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("Missing SECRET_KEY environment variable!")

    # Session config
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)

    # Security headers
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        "Content-Security-Policy": (
            "default-src 'self' https://cdnjs.cloudflare.com https://www.instagram.com; "
            "img-src 'self' https://www.instagram.com data:; "
            "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
            "script-src 'self' 'unsafe-inline';"
        )
    }

    # Rate limiting
    RATELIMIT_DEFAULT = "200 per day"
    RATELIMIT_STORAGE_URL = "memory://"

    # Instagram API limits
    INSTAGRAM_LIMITS = {
        'likes_per_day': 300,
        'follows_per_day': 100,
        'unfollows_per_day': 100,
        'comments_per_day': 50,
        'dms_per_day': 50
    }

    # Logging
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_LEVEL = logging.INFO  # Using logging.INFO instead of a string
    LOG_FILE = "instagram_bot.log"

class DevelopmentConfig(Config):
    """Development-specific configuration."""
    
    DEBUG = True
    DEVELOPMENT = True

class ProductionConfig(Config):
    """Production-specific configuration with enhanced security."""

    DEBUG = False
    DEVELOPMENT = False

    # Production security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Use Redis for session storage in production
    REDIS_URL = os.environ.get("REDIS_URL")
    if REDIS_URL:
        SESSION_TYPE = "redis"
        SESSION_REDIS = redis.from_url(REDIS_URL)
        RATELIMIT_STORAGE_URL = REDIS_URL

# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}
