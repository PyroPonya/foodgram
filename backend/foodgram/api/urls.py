# flake8: noqa
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import (
    UserViewSet,
)

app_name = 'api'

router = DefaultRouter()
# router.register(
#     r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
#     CommentViewSet, basename='comments')


router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken'))
]
# /api/ > auth/ > token/login/
# from djoser.views import UserViewSet
