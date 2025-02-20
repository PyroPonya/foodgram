from django.shortcuts import redirect
from django.views import View

from .models import Recipe


class RecipeRedirectView(View):
    """Перенаправление на страницу рецепта."""

    def get(self, request, pk=None):
        """Перенаправление на страницу рецепта."""
        if not Recipe.objects.filter(pk=pk).exists():
            return redirect('/404/')
        return redirect(f'/recipes/{pk}/')
