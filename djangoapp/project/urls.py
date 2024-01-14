"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from rest_framework import routers

from hello_world_api.views import JsonArrayOfDOUViewSet
from trigger_web_scraping_dou_api.views import ScraperViewSet
from trigger_web_scraping_dou_api.views import JournalJsonArrayOfDOUViewSet


router = routers.DefaultRouter()
# router.register(r'jsonarrayofdou', JsonArrayOfDOUViewSet)
router.register(r'journaljsonarrayofdouviewset', JournalJsonArrayOfDOUViewSet)

urlpatterns = [
    path('', include('hello_world.urls')),
    path('admin/', admin.site.urls),
    # path('api/', include(router.urls)),
    path('trigger_web_scraping_dou_api/', ScraperViewSet.as_view(), name='scraperviewset'),
    path('db_dou_api/', include(router.urls)),
]

# Para poder ver os arquivos de media em time real quando o cliente enviar post
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
        
    )
    
    import debug_toolbar
    urlpatterns += [path("__debug__/", include(debug_toolbar.urls)),]