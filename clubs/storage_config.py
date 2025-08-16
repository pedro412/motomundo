# Storage configuration settings for different environments
import os

# Helper function to get environment variables with defaults
def config(key, default=None, cast=None):
    """Simple config helper - replace with python-decouple in production"""
    value = os.environ.get(key, default)
    if cast and value is not None:
        if cast == bool:
            if isinstance(value, bool):
                return value
            return str(value).lower() in ('true', '1', 'yes', 'on')
        return cast(value)
    return value

# =============================================================================
# IMAGE STORAGE BACKEND SELECTION
# =============================================================================

# Current storage backend - can be switched without code changes
# Options: 'cloudinary', 's3', 'local'
IMAGE_STORAGE_BACKEND = config('IMAGE_STORAGE_BACKEND', default='cloudinary')

# =============================================================================
# CLOUDINARY CONFIGURATION
# =============================================================================

# Cloudinary settings (for current phase)
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME', default=''),
    'API_KEY': config('CLOUDINARY_API_KEY', default=''),
    'API_SECRET': config('CLOUDINARY_API_SECRET', default=''),
    'SECURE': True,  # Use HTTPS
    'FOLDER': 'motomundo',  # Organize files in a folder
    'TRANSFORMATION': {
        'quality': 'auto:best',  # Automatic quality optimization
        'fetch_format': 'auto',  # Automatic format selection (WebP, etc.)
    }
}

# Profile picture specific transformations
CLOUDINARY_PROFILE_TRANSFORMATIONS = {
    'thumbnail': {'width': 150, 'height': 150, 'crop': 'fill', 'gravity': 'face'},
    'medium': {'width': 300, 'height': 300, 'crop': 'fill', 'gravity': 'face'},
    'large': {'width': 600, 'height': 600, 'crop': 'limit'},
}

# =============================================================================
# AWS S3 CONFIGURATION (for future migration)
# =============================================================================

# AWS S3 settings (will be used when migrating from Cloudinary)
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='motomundo-media')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
AWS_S3_CUSTOM_DOMAIN = config('AWS_S3_CUSTOM_DOMAIN', default='')  # CloudFront domain
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',  # 1 day cache
}
AWS_S3_FILE_OVERWRITE = False
AWS_LOCATION = 'media'

# =============================================================================
# STORAGE MONITORING CONFIGURATION
# =============================================================================

# Enable storage usage tracking
ENABLE_STORAGE_MONITORING = config('ENABLE_STORAGE_MONITORING', default=True, cast=bool)

# Storage cost alert thresholds (in USD)
STORAGE_COST_ALERT_THRESHOLD = config('STORAGE_COST_ALERT_THRESHOLD', default=80, cast=int)

# Migration recommendation threshold (when to suggest S3)
MIGRATION_THRESHOLD_USERS = config('MIGRATION_THRESHOLD_USERS', default=150, cast=int)
MIGRATION_THRESHOLD_SIZE_GB = config('MIGRATION_THRESHOLD_SIZE_GB', default=20, cast=int)

# =============================================================================
# ENVIRONMENT-SPECIFIC DEFAULTS
# =============================================================================

def get_storage_settings_for_environment():
    """
    Return appropriate storage settings based on environment
    """
    environment = config('DJANGO_ENV', default='development')
    
    if environment == 'production':
        return {
            'IMAGE_STORAGE_BACKEND': 'cloudinary',
            'USE_CLOUDINARY_CDN': True,
            'ENABLE_IMAGE_OPTIMIZATION': True,
        }
    elif environment == 'staging':
        return {
            'IMAGE_STORAGE_BACKEND': 'cloudinary',
            'USE_CLOUDINARY_CDN': True,
            'ENABLE_IMAGE_OPTIMIZATION': False,  # Faster uploads for testing
        }
    else:  # development
        return {
            'IMAGE_STORAGE_BACKEND': 'local',
            'USE_CLOUDINARY_CDN': False,
            'ENABLE_IMAGE_OPTIMIZATION': False,
        }

# Apply environment-specific settings
ENV_STORAGE_SETTINGS = get_storage_settings_for_environment()
