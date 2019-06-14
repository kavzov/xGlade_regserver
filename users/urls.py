from django.conf.urls import url
from users import views
from djoser import views as djoser_views
from django.contrib.auth import get_user_model


User = get_user_model()


urlpatterns = [
    url(r'^$', views.RootView.as_view(), name='root'),
    url(
        r'^api/user/create/?$',
        views.UserCreateView.as_view(),
        name='create user'
    ),
    url(
        r'^api/user/(?P<pk>\d+)/?$',
        views.UserDetailView.as_view(),
        name='user details'
    ),
    url(
        r'^api/user/me/?$',
        views.CurrentUserDetailView.as_view(),
        name='current user details'
    ),
    url(
        r'^api/users/?$',
        views.UsersListView.as_view(),
        name='users list'
    ),
    url(
        r'^api/user/login/?$',
        djoser_views.TokenCreateView.as_view(),
        name='login'
    ),
    url(
        r'^api/user/logout/?$',
        djoser_views.TokenDestroyView.as_view(),
        name='logout'
    ),
    url(
        r'^api/token/get/?$',
        djoser_views.TokenCreateView.as_view(),
        name='get token'
    ),
    url(
        r'^api/user/{0}/?$'.format(User.USERNAME_FIELD),
        views.djoser_views.SetUsernameView.as_view(),
        name='set username'
    ),
    url(
        r'^api/user/password/?$',
        djoser_views.SetPasswordView.as_view(),
        name='set password'),
]
