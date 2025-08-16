# Storage backends for flexible file storage strategy
import os
import logging
from django.conf import settings
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseImageStorage(Storage, ABC):
    """
    Abstract base class for image storage backends.
    This ensures all storage implementations have the same interface.
    """
    
    @abstractmethod
    def save(self, name, content, max_length=None):
        """Save a file and return the storage path"""
        pass
    
    @abstractmethod
    def url(self, name):
        """Return the URL for accessing the file"""
        pass
    
    @abstractmethod
    def delete(self, name):
        """Delete a file"""
        pass
    
    @abstractmethod
    def exists(self, name):
        """Check if a file exists"""
        pass
    
    @abstractmethod
    def size(self, name):
        """Return the size of a file"""
        pass


class CloudinaryImageStorage(BaseImageStorage):
    """
    Cloudinary storage implementation with optimization settings
    """
    
    def __init__(self):
        self.backend_type = 'cloudinary'
        try:
            from cloudinary_storage.storage import MediaCloudinaryStorage
            self.storage = MediaCloudinaryStorage()
            logger.info("Cloudinary storage initialized successfully")
        except ImportError:
            logger.error("Cloudinary not installed. Run: pip install django-cloudinary-storage")
            raise
    
    def save(self, name, content, max_length=None):
        """Save with automatic optimization for profile pictures"""
        return self.storage.save(name, content, max_length)
    
    def url(self, name):
        """Return optimized Cloudinary URL"""
        return self.storage.url(name)
    
    def delete(self, name):
        return self.storage.delete(name)
    
    def exists(self, name):
        return self.storage.exists(name)
    
    def size(self, name):
        return self.storage.size(name)
    
    def _open(self, name, mode='rb'):
        return self.storage._open(name, mode)
    
    def _save(self, name, content):
        return self.storage._save(name, content)
    
    def get_accessed_time(self, name):
        return self.storage.get_accessed_time(name)
    
    def get_created_time(self, name):
        return self.storage.get_created_time(name)
    
    def get_modified_time(self, name):
        return self.storage.get_modified_time(name)


class S3ImageStorage(BaseImageStorage):
    """
    AWS S3 storage implementation (for future migration)
    """
    
    def __init__(self):
        self.backend_type = 's3'
        try:
            from storages.backends.s3boto3 import S3Boto3Storage
            
            class ProfilePictureS3Storage(S3Boto3Storage):
                bucket_name = settings.AWS_STORAGE_BUCKET_NAME
                location = 'members/profiles'
                default_acl = 'public-read'
                file_overwrite = False
                custom_domain = getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', None)
            
            self.storage = ProfilePictureS3Storage()
            logger.info("S3 storage initialized successfully")
        except ImportError:
            logger.error("AWS storage not installed. Run: pip install django-storages[s3]")
            raise
    
    def save(self, name, content, max_length=None):
        return self.storage.save(name, content, max_length)
    
    def url(self, name):
        return self.storage.url(name)
    
    def delete(self, name):
        return self.storage.delete(name)
    
    def exists(self, name):
        return self.storage.exists(name)
    
    def size(self, name):
        return self.storage.size(name)


class LocalImageStorage(BaseImageStorage):
    """
    Local storage fallback (for development)
    """
    
    def __init__(self):
        self.backend_type = 'local'
        from django.core.files.storage import default_storage
        self.storage = default_storage
        logger.info("Local storage initialized")
    
    def save(self, name, content, max_length=None):
        return self.storage.save(name, content, max_length)
    
    def url(self, name):
        return self.storage.url(name)
    
    def delete(self, name):
        return self.storage.delete(name)
    
    def exists(self, name):
        return self.storage.exists(name)
    
    def size(self, name):
        return self.storage.size(name)
    
    def _open(self, name, mode='rb'):
        return self.storage._open(name, mode)
    
    def _save(self, name, content):
        return self.storage._save(name, content)
    
    def get_accessed_time(self, name):
        return self.storage.get_accessed_time(name)
    
    def get_created_time(self, name):
        return self.storage.get_created_time(name)
    
    def get_modified_time(self, name):
        return self.storage.get_modified_time(name)


class FlexibleImageStorage(Storage):
    """
    Storage manager that automatically selects the appropriate backend
    based on configuration. This makes migration between services seamless.
    """
    
    def __init__(self):
        self.backend_type = getattr(settings, 'IMAGE_STORAGE_BACKEND', 'local')
        self._storage = None
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize the appropriate storage backend"""
        try:
            if self.backend_type == 'cloudinary':
                self._storage = CloudinaryImageStorage()
            elif self.backend_type == 's3':
                self._storage = S3ImageStorage()
            else:
                self._storage = LocalImageStorage()
                
            logger.info(f"Storage backend initialized: {self.backend_type}")
            
        except Exception as e:
            logger.error(f"Failed to initialize {self.backend_type} storage: {e}")
            # Fallback to local storage
            self._storage = LocalImageStorage()
            logger.info("Falling back to local storage")
    
    def save(self, name, content, max_length=None):
        """Save a file using the configured backend"""
        try:
            return self._storage.save(name, content, max_length)
        except Exception as e:
            logger.error(f"Error saving file {name}: {e}")
            raise
    
    def url(self, name):
        """Get file URL using the configured backend"""
        try:
            return self._storage.url(name)
        except Exception as e:
            logger.error(f"Error getting URL for {name}: {e}")
            return None
    
    def delete(self, name):
        """Delete a file using the configured backend"""
        try:
            return self._storage.delete(name)
        except Exception as e:
            logger.error(f"Error deleting file {name}: {e}")
            return False
    
    def exists(self, name):
        """Check if file exists using the configured backend"""
        try:
            return self._storage.exists(name)
        except Exception as e:
            logger.error(f"Error checking existence of {name}: {e}")
            return False
    
    def size(self, name):
        """Get file size using the configured backend"""
        try:
            return self._storage.size(name)
        except Exception as e:
            logger.error(f"Error getting size of {name}: {e}")
            return 0
    
    def _open(self, name, mode='rb'):
        """Open a file for reading using the configured backend"""
        try:
            return self._storage._open(name, mode)
        except Exception as e:
            logger.error(f"Error opening file {name}: {e}")
            raise
    
    def _save(self, name, content):
        """Save a file using the configured backend"""
        try:
            return self._storage._save(name, content)
        except Exception as e:
            logger.error(f"Error saving file {name}: {e}")
            raise
    
    def get_accessed_time(self, name):
        """Get file accessed time"""
        try:
            return self._storage.get_accessed_time(name)
        except Exception as e:
            logger.error(f"Error getting accessed time for {name}: {e}")
            return None
    
    def get_created_time(self, name):
        """Get file created time"""
        try:
            return self._storage.get_created_time(name)
        except Exception as e:
            logger.error(f"Error getting created time for {name}: {e}")
            return None
    
    def get_modified_time(self, name):
        """Get file modified time"""
        try:
            return self._storage.get_modified_time(name)
        except Exception as e:
            logger.error(f"Error getting modified time for {name}: {e}")
            return None


# Function to get storage instance (migration-friendly)
def get_flexible_image_storage():
    """Returns the flexible image storage instance. Migration-friendly."""
    return FlexibleImageStorage()

# Create a singleton instance for easy importing
flexible_image_storage = get_flexible_image_storage()

# Migration-friendly storage class path string
FLEXIBLE_STORAGE_PATH = 'clubs.storage_backends.get_flexible_image_storage'


# Usage tracking for cost monitoring
class StorageMetrics:
    """
    Track storage usage to help with migration decisions
    """
    
    @staticmethod
    def get_total_storage_usage():
        """Calculate total storage usage across all members"""
        from clubs.models import Member
        
        total_size = 0
        file_count = 0
        
        for member in Member.objects.filter(profile_picture__isnull=False):
            try:
                if member.profile_picture:
                    total_size += member.profile_picture.size
                    file_count += 1
            except (OSError, ValueError):
                # File doesn't exist or is corrupted
                pass
        
        return {
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'file_count': file_count,
            'avg_file_size_mb': round((total_size / file_count) / (1024 * 1024), 2) if file_count > 0 else 0
        }
    
    @staticmethod
    def estimate_monthly_costs():
        """Estimate monthly costs for current usage"""
        usage = StorageMetrics.get_total_storage_usage()
        
        # Cloudinary pricing (simplified)
        cloudinary_cost = 0 if usage['total_size_mb'] < 25000 else 99  # $99 for advanced plan
        
        # AWS S3 pricing (simplified: $0.023/GB + bandwidth)
        storage_gb = usage['total_size_mb'] / 1024
        s3_storage_cost = max(0, storage_gb * 0.023)  # After free tier
        s3_bandwidth_cost = storage_gb * 0.09  # Estimate bandwidth as 1x storage per month
        s3_total = s3_storage_cost + s3_bandwidth_cost + 50  # +$50 for CloudFront
        
        return {
            'current_usage': usage,
            'cloudinary_cost': cloudinary_cost,
            's3_estimated_cost': round(s3_total, 2),
            'recommendation': 'cloudinary' if cloudinary_cost <= s3_total else 's3'
        }


# Migration utilities
class StorageMigrator:
    """
    Utilities for migrating between storage backends
    """
    
    @staticmethod
    def migrate_cloudinary_to_s3():
        """
        Migrate files from Cloudinary to S3
        This would be used when scaling beyond Cloudinary's cost efficiency
        """
        # Implementation would:
        # 1. Download files from Cloudinary
        # 2. Upload to S3
        # 3. Update database URLs
        # 4. Verify migration
        # 5. Clean up Cloudinary
        pass
    
    @staticmethod
    def test_storage_backend():
        """Test current storage backend is working"""
        try:
            storage = FlexibleImageStorage()
            # Test with a small file
            test_content = b"test image content"
            from django.core.files.base import ContentFile
            test_file = ContentFile(test_content, name="test.jpg")
            
            # Save test file
            path = storage.save("test/storage_test.jpg", test_file)
            
            # Verify it exists and can be accessed
            url = storage.url(path)
            exists = storage.exists(path)
            
            # Clean up
            storage.delete(path)
            
            return {
                'status': 'success',
                'backend': storage.backend_type,
                'test_url': url,
                'exists': exists
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
