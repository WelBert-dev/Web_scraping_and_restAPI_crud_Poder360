from datetime import datetime
from trigger_web_scraping_dou_api.models import JournalJsonArrayOfDOU

class JournalJsonArrayOfDOUService:

    @staticmethod
    def insert_into_distinct_with_dict(dou_journals_jsonArrayField_dict):
        dou_journals_jsonArrayField_list = [JournalJsonArrayOfDOU(**item) for item in dou_journals_jsonArrayField_dict]
                        
        # Antes de chamar bulk_create, transformação nos dados normalizando no padrão YYYY-MM-DD
        for single_dou_journal in dou_journals_jsonArrayField_list:
            single_dou_journal.pubDate = datetime.strptime(single_dou_journal.pubDate, "%d/%m/%Y").strftime("%Y-%m-%d")
        
        
        dou_journals_toBe_insert = [
            JournalJsonArrayOfDOU(
                urlTitle=obj.urlTitle,
                pubName=obj.pubName,
                numberPage=obj.numberPage,
                subTitulo=obj.subTitulo,
                titulo=obj.titulo,
                title=obj.title,
                pubDate=obj.pubDate,
                content=obj.content,
                editionNumber=obj.editionNumber,
                hierarchyLevelSize=obj.hierarchyLevelSize,
                artType=obj.artType,
                pubOrder=obj.pubOrder,
                hierarchyStr=obj.hierarchyStr,
                hierarchyList=obj.hierarchyList
            )
            for obj in dou_journals_jsonArrayField_list
        ]

        # Verifique quais objetos já existem no banco de dados
        existing_record = JournalJsonArrayOfDOU.objects.filter(urlTitle__in=[obj.urlTitle for obj in dou_journals_toBe_insert])

        # Remova os objetos existentes da lista para evitar a duplicação
        dou_journals_toBe_insert = [obj for obj in dou_journals_toBe_insert if obj.urlTitle not in existing_record.values_list('urlTitle', flat=True)]

        # Use bulk_create para inserir os objetos restantes
        JournalJsonArrayOfDOU.objects.bulk_create(dou_journals_toBe_insert) 
    