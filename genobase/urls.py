"""genobase URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
# from django.urls import path
#
# urlpatterns = [
#     path('admin/', admin.site.urls),
# ]


from rest_framework import routers

from async_job.views import AsyncJobViewSet
from gene_parser.views import GeneParserViewSet


router = routers.SimpleRouter()

router.register(
    'gene_parser',
    GeneParserViewSet,
)

router.register(
    'async_job',
    AsyncJobViewSet,
)

urlpatterns = router.urls
