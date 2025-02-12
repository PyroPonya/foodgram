from rest_framework import routers
from django.urls import include, path
from .views import IngredientViewSet, RecipeViewSet, TagViewSet

app_name = 'food'

router = routers.DefaultRouter()
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
