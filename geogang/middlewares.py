from django.utils import translation
from django.conf import settings

class LanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        translation.activate(settings.LANGUAGE_CODE)  # or your language code
        response = self.get_response(request)
        translation.deactivate()
        return response