from rest_framework_simplejwt.views import TokenRefreshView

class MyTokenRefreshView(TokenRefreshView):
    serializer_class = MyTokenRefreshSerializer
