from hello_world_api.serializers import JsonArrayOfDOUSerializer
from hello_world_api.models import JsonArrayOfDOU
from rest_framework import viewsets



class JsonArrayOfDOUViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows JsonArrayOfDOU to be viewed or edited.
    """
    queryset = JsonArrayOfDOU.objects.all()
    serializer_class = JsonArrayOfDOUSerializer

