from hello_world_api.models import JsonArrayOfDOU
from rest_framework import serializers


class JsonArrayOfDOUSerializer(serializers.ModelSerializer):
    class Meta:
        model = JsonArrayOfDOU
        fields = (
            'id', 'pubName', 'urlTitle', 'numberPage', 'subTitulo', 'titulo',
            'title', 'pubDate', 'content', 'editionNumber', 'hierarchyLevelSize',
            'artType', 'pubOrder', 'hierarchyStr', 'hierarchyList'
        )

