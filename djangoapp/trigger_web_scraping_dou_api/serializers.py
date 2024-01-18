from trigger_web_scraping_dou_api.models import JournalJsonArrayOfDOU
from trigger_web_scraping_dou_api.models import DetailSingleJournalOfDOU

from rest_framework import serializers


class JournalJsonArrayOfDOUSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalJsonArrayOfDOU
        fields = (
            'id', 
            'pubName', 
            'urlTitle', 
            'numberPage', 
            'subTitulo', 
            'titulo',
            'title', 
            'pubDate', 
            'content', 
            'editionNumber', 
            'hierarchyLevelSize',
            'artType', 
            'pubOrder', 
            'hierarchyStr', 
            'hierarchyList'
        )


class DetailSingleJournalOfDOUSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetailSingleJournalOfDOU
        fields = (
            'id',
            'versao_certificada',
            'publicado_dou_data',
            'edicao_dou_data',
            'secao_dou_data',
            'orgao_dou_data',
            'title',
            'paragrafos',
            'assina',
            'cargo',
        )

