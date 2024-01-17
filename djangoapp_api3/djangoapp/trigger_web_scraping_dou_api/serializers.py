from trigger_web_scraping_dou_api.models import JournalJsonArrayOfDOU
from rest_framework import serializers


class JournalJsonArrayOfDOUSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalJsonArrayOfDOU
        fields = (
            'id', 'pubName', 'urlTitle', 'numberPage', 'subTitulo', 'titulo',
            'title', 'pubDate', 'content', 'editionNumber', 'hierarchyLevelSize',
            'artType', 'pubOrder', 'hierarchyStr', 'hierarchyList'
        )

