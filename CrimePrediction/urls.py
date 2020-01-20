from django.urls import path, include
from rest_framework import routers
from .views import SafeUnsafe, LocationViewSet, RatingViewSet, UserViewSet

router = routers.DefaultRouter()
router.register('users', UserViewSet)
router.register('locations', LocationViewSet)
router.register('ratings', RatingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('prediction/', SafeUnsafe),
]