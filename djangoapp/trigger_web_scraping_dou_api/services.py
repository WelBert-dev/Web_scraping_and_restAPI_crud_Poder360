from datetime import datetime
from trigger_web_scraping_dou_api.models import JournalJsonArrayOfDOU

class JournalJsonArrayOfDOUService:

    @staticmethod
    def insert_into_distinct_with_dict(dou_journals_jsonArrayField_dict):
        
        # print("LEN NO BANCO: ", JournalJsonArrayOfDOU.objects.count())
        # print("LEN A SER INSERIDO: ", len(dou_journals_jsonArrayField_dict))
        
        # Otimização para ganho de performance, mas não garante 100% elemento a elemento... porisso resolvi retirar 
        # Utilizar count é muito genérico e não garante que são os mesmos registros... 
        
        # records_inDB_count = JournalJsonArrayOfDOU.objects.count()
        # records_toBe_insert_count = len(dou_journals_jsonArrayField_dict)
        
        # if records_inDB_count != records_toBe_insert_count:
            
        
        dou_journals_jsonArrayField_list = [JournalJsonArrayOfDOU(**item) for item in dou_journals_jsonArrayField_dict]
        
                        
        # Antes de chamar bulk_create, transformação nos dados normalizando no padrão YYYY-MM-DD
        # E aproveita o mesmo looping para 
        for single_dou_journal in dou_journals_jsonArrayField_list:
            single_dou_journal.pubDate = datetime.strptime(single_dou_journal.pubDate, "%d/%m/%Y").strftime("%Y-%m-%d")

        # Verifique quais objetos já existem no banco de dados
        existing_record = JournalJsonArrayOfDOU.objects.filter(urlTitle__in=[obj.urlTitle for obj in dou_journals_jsonArrayField_list])
        
        # Remova os objetos existentes da lista para evitar a duplicação
        dou_journals_jsonArrayField_list = [obj for obj in dou_journals_jsonArrayField_list if obj.urlTitle not in existing_record.values_list('urlTitle', flat=True)]
        
        # Use bulk_create para inserir os objetos restantes
        JournalJsonArrayOfDOU.objects.bulk_create(dou_journals_jsonArrayField_list) 
    