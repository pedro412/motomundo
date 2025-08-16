# Management command to test storage backend functionality
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from clubs.storage_backends import flexible_image_storage
import tempfile
from PIL import Image
import io


class Command(BaseCommand):
    help = 'Test the current storage backend configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--backend',
            help='Specific backend to test (cloudinary, s3, local)'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🧪 Testing Storage Backend')
        )
        self.stdout.write('=' * 40)
        
        try:
            # Test current storage backend
            result = self._test_storage_operations()
            
            if result['status'] == 'success':
                self.stdout.write(
                    self.style.SUCCESS('✅ Storage backend test passed!')
                )
                self.stdout.write(f"   Backend: {result['backend']}")
                self.stdout.write(f"   Test file URL: {result['test_url']}")
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Storage backend test failed: {result["error"]}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error testing storage: {e}')
            )

    def _test_storage_operations(self):
        """Test basic storage operations"""
        try:
            # Create a test image
            test_image = self._create_test_image()
            
            # Test save operation
            path = flexible_image_storage.save("test/storage_test.jpg", test_image)
            self.stdout.write(f"✅ Save operation: {path}")
            
            # Test URL generation
            url = flexible_image_storage.url(path)
            self.stdout.write(f"✅ URL generation: {url}")
            
            # Test exists check
            exists = flexible_image_storage.exists(path)
            self.stdout.write(f"✅ Exists check: {exists}")
            
            # Test size check
            try:
                size = flexible_image_storage.size(path)
                self.stdout.write(f"✅ Size check: {size} bytes")
            except:
                self.stdout.write("⚠️  Size check not available for this backend")
            
            # Test delete operation
            flexible_image_storage.delete(path)
            self.stdout.write(f"✅ Delete operation completed")
            
            return {
                'status': 'success',
                'backend': flexible_image_storage.backend_type,
                'test_url': url
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def _create_test_image(self):
        """Create a small test image"""
        # Create a 100x100 red square
        img = Image.new('RGB', (100, 100), color='red')
        
        # Convert to bytes
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='JPEG')
        img_buffer.seek(0)
        
        return ContentFile(img_buffer.getvalue(), name='test_image.jpg')
