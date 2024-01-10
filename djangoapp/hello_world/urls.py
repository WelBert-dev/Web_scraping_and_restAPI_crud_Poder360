from django.urls import path
from hello_world.views import index

app_name = 'hello_world'

urlpatterns = [
    # hello_world:index
    path('', index, name='index'),
]
