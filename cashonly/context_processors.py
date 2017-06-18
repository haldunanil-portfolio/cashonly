from django.conf import settings  # import the settings file


def server_mode(request):
    return {'SERVER_MODE': settings.SERVER_MODE}
