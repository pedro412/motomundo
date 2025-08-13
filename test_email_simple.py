#!/usr/bin/env python
"""
Simple test for email template rendering without database dependencies
"""
import os
import sys
from pathlib import Path

# Add project directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set up minimal Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motomundo.settings')

# Override database settings for this test
import django
from django.conf import settings

# Mock database settings for testing
test_settings = {
    'DATABASES': {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    },
    'USE_TZ': True,
    'SECRET_KEY': 'test-secret-key',
    'DEBUG': True,
    'INSTALLED_APPS': [
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'emails',
        'clubs',
    ],
    'TEMPLATES': [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                ],
            },
        },
    ],
    'EMAIL_BACKEND': 'django.core.mail.backends.console.EmailBackend',
}

# Configure Django with test settings
if not settings.configured:
    settings.configure(**test_settings)

django.setup()

from django.template.loader import render_to_string
from django.core.mail import send_mail

def test_email_template():
    """Test email template rendering"""
    print("🧪 Testing Spanish email invitation template...")
    
    # Mock context data
    context = {
        'nombre_prospecto': 'Miguel Gutierrez',
        'nombre_club': 'Nacional MC',
        'nombre_chapter': 'Bogotá Chapter',
        'nombre_padrino': 'Carlos Rodriguez',
        'rol': 'Miembro',
        'token': 'abc123def456',
        'url_aceptar': 'https://motomundo.example.com/invitations/accept/abc123def456',
        'url_rechazar': 'https://motomundo.example.com/invitations/decline/abc123def456',
        'fecha_expira': '15 de Septiembre, 2025',
        'mensaje_personal': 'Hermano, sabemos que eres un motociclista de corazón y nos encantaría tenerte en nuestra familia. Tu experiencia y pasión por las dos ruedas serían una gran adición a nuestro chapter.',
    }
    
    try:
        # Test text template
        text_content = render_to_string('emails/invitacion.txt', context)
        print("✅ Text template rendered successfully")
        print("📧 Text email content:")
        print("-" * 50)
        print(text_content)
        print("-" * 50)
        
        # Test HTML template
        html_content = render_to_string('emails/invitacion.html', context)
        print("✅ HTML template rendered successfully")
        print("📧 HTML email content preview:")
        print("-" * 50)
        print(html_content[:300] + "..." if len(html_content) > 300 else html_content)
        print("-" * 50)
        
        # Test sending email to console
        print("📤 Testing email sending...")
        send_mail(
            subject=f'Invitación a {context["nombre_club"]} - {context["nombre_chapter"]}',
            message=text_content,
            from_email='invitaciones@motomundo.com',
            recipient_list=['test@example.com'],
            html_message=html_content,
        )
        print("✅ Email sent successfully to console backend")
        
    except Exception as e:
        print(f"❌ Error testing email template: {e}")
        return False
    
    return True

if __name__ == '__main__':
    print("🏍️  MotoMundo Email Invitation System Test")
    print("=" * 50)
    
    success = test_email_template()
    
    if success:
        print("\n🎉 All email tests passed!")
        print("📝 Next steps:")
        print("   1. Configure SMTP settings for production")
        print("   2. Set up Railway environment variables")
        print("   3. Test with real database connection")
    else:
        print("\n💥 Some tests failed. Check the errors above.")
        sys.exit(1)
