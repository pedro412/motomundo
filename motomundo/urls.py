from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from clubs.api import ClubViewSet, ChapterViewSet, MemberViewSet, ClubAdminViewSet, ChapterManagerViewSet
from .health import healthz
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'clubs', ClubViewSet)
router.register(r'chapters', ChapterViewSet)
router.register(r'members', MemberViewSet)
router.register(r'club-admins', ClubAdminViewSet)
router.register(r'chapter-managers', ChapterManagerViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('clubs/', include('clubs.urls')),
    path('api/', include(router.urls)),
    path('api/auth/', include('clubs.auth_urls')),
    path('healthz', healthz),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
