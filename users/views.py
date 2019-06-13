from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from users.models import User
from djoser import utils, signals
from djoser.conf import settings
from djoser.compat import get_user_email
from djoser import views as djoser_views


class UserCreateMixin:
    @staticmethod
    def _login_on_create_settings():
        return settings.LOGIN_ON_USER_CREATE and \
               not (settings.SEND_ACTIVATION_EMAIL or settings.SEND_CONFIRMATION_EMAIL)

    def perform_create(self, serializer):
        user = serializer.save()
        signals.user_registered.send(
            sender=self.__class__, user=user, request=self.request
        )
        context = {'user': user}
        to = [get_user_email(user)]
        if settings.SEND_ACTIVATION_EMAIL:
            settings.EMAIL.activation(self.request, context).send(to)
        elif settings.SEND_CONFIRMATION_EMAIL:
            settings.EMAIL.confirmation(self.request, context).send(to)

        return user

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        response_data = serializer.data
        if self._login_on_create_settings():
            token = utils.login_user(request, user)
            response_data['token'] = str(token)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)


class UserCreateView(UserCreateMixin, generics.CreateAPIView):
    """
    Use this endpoint to register new user.
    """
    permission_classes = settings.PERMISSIONS.user_create
    if UserCreateMixin._login_on_create_settings():
        permission_classes += settings.PERMISSIONS.token_create

    def get_serializer_class(self):
        if settings.USER_CREATE_PASSWORD_RETYPE:
            return settings.SERIALIZERS.user_create_password_retype
        return settings.SERIALIZERS.user_create


class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = settings.SERIALIZERS.user
    permission_classes = settings.PERMISSIONS.user


class CurrentUserDetailView(djoser_views.UserView):
    serializer_class = settings.SERIALIZERS.current_user
    permission_classes = settings.PERMISSIONS.current_user


class UsersListView(generics.ListAPIView):
    permission_classes = settings.PERMISSIONS.users
    queryset = User.objects.raw(
        "WITH summary AS (SELECT *, row_number() OVER (order by rating desc, username) AS pos FROM users) "
        "SELECT pos, username, rating, battles, won, id FROM summary;"
    )
    serializer_class = settings.SERIALIZERS.users


class RootView(djoser_views.RootView):
    def aggregate_djoser_urlpattern_names(self):
        from users import urls
        urlpattern_names = self._get_url_names(urls.urlpatterns)
        return urlpattern_names

    def get(self, request, fmt=None):
        urlpattern_names = self.aggregate_djoser_urlpattern_names()
        urls_map = {
            title: url for (title, url)
            in self.get_urls_map(request, urlpattern_names, fmt).items()
            if url != ''   # skip empty urls (not passed through django reverse())
        }

        return Response(urls_map)
