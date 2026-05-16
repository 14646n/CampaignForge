from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.campaigns.views import CampaignViewSet, SessionViewSet, CharacterViewSet

router = DefaultRouter()
router.register(r'campaigns', CampaignViewSet)
router.register(r'sessions', SessionViewSet)
router.register(r'characters', CharacterViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]