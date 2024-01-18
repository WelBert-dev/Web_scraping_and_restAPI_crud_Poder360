from datetime import datetime
from trigger_web_scraping_dou_api.models import JournalJsonArrayOfDOU, DetailSingleJournalOfDOU

from django.db import IntegrityError, transaction

from itertools import chain

class JournalJsonArrayOfDOUService:

    @staticmethod
    def insert_into_distinct_journals_and_date_normalize(dou_journals_jsonArrayField_dict):
        
        dous_normalized_list = []
        
        # Achata a lista em apenas uma, estilo "flatMap" dos fluxos streams no Java:
        # Achatar é unir todos os objetos da lista interna em apenas uma.
        flat_list = []
        if isinstance(dou_journals_jsonArrayField_dict, list): # QUando tem do1, do2 e do3
            if len(dou_journals_jsonArrayField_dict) == 3:
                flat_list = [item for sublist in dou_journals_jsonArrayField_dict for inner_list in sublist for item in inner_list]
            else:
                
                flat_list = list(chain.from_iterable(dou_journals_jsonArrayField_dict))

        elif isinstance(dou_journals_jsonArrayField_dict, dict):
            
            dict_list = list(dou_journals_jsonArrayField_dict.values())
            
            flat_list = list(chain.from_iterable(dict_list))
            
        for single_dou_journal_value in flat_list:
            single_dou_journal_value['pubDate'] = datetime.strptime(single_dou_journal_value['pubDate'], "%d/%m/%Y").strftime("%Y-%m-%d")
            dous_normalized_list.append(single_dou_journal_value)
           
        # ignore_conflicts=True continua a inserir os objetos em cascata e quando encontra duplicatas não insere (ignora esse elemento) e continua operação..
        # Removi mais verificações para ganho de performance. (Desta forma esta resolvendo bem e não está duplicado, mais testes vão ser implementados no tests.py depois)
        JournalJsonArrayOfDOU.objects.bulk_create([JournalJsonArrayOfDOU(**item) for item in dous_normalized_list], ignore_conflicts=True)
        
        

class DetailSingleJournalOfDOUService:

    @staticmethod
    def insert_into_distinct_journals_and_date_normalize(details_dou_journals_dict):
        
        created_objects = []
        print(details_dou_journals_dict)
        for record in details_dou_journals_dict:
            record['publicado_dou_data'] = datetime.strptime(record['publicado_dou_data'], "%d/%m/%Y").strftime("%Y-%m-%d")

            try:
                with transaction.atomic():
                    obj = DetailSingleJournalOfDOU.objects.create(**record)
                    created_objects.append(obj)
            except IntegrityError as e:
                print("ERRO AO ISERIR: ",e)
                print("Objetos inseridos com sucesso: ", created_objects)
                pass

    