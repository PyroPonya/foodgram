"""urls.py."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    SignupView,
    TitleViewSet,
    TokenObtainView,
    UserViewSet,
)

v1_router = DefaultRouter()
v1_router.register('categories', CategoryViewSet, basename='categories')
v1_router.register('genres', GenreViewSet, basename='genres')
v1_router.register('titles', TitleViewSet, basename='titles')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet, basename='reviews')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments')
v1_router.register('users', UserViewSet, basename='users')

auth_urls = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('token/', TokenObtainView.as_view(), name='token-obtain')
]

v1_urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/', include(auth_urls))
]
urlpatterns = [
    path('v1/', include(v1_urlpatterns)),
]
