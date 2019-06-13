from django.contrib import admin
from django.conf.urls import url, include
from users import urls


urlpatterns = [
    url(r'^admin', admin.site.urls),
    url(r'^', include(urls))
]
