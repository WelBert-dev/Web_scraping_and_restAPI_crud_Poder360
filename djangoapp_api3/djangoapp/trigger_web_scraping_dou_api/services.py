from datetime import datetime
from trigger_web_scraping_dou_api.models import JournalJsonArrayOfDOU

class JournalJsonArrayOfDOUService:

    @staticmethod
    def insert_into_distinct_journals_and_date_normalize(dou_journals_jsonArrayField_dict):
        
        for single_dou_journal_value in dou_journals_jsonArrayField_dict:
            # Normaliza a data no formato do db
            single_dou_journal_value['pubDate'] = datetime.strptime(single_dou_journal_value['pubDate'], "%d/%m/%Y").strftime("%Y-%m-%d")

        # ignore_conflicts=True continua a inserir os objetos em cascata e quando encontra duplicatas não insere (ignora esse elemento) e continua operação..
        # Removi mais verificações para ganho de performance. (Desta forma esta resolvendo bem e não está duplicado, mais testes vão ser implementados no tests.py depois)
        JournalJsonArrayOfDOU.objects.bulk_create([JournalJsonArrayOfDOU(**item) for item in dou_journals_jsonArrayField_dict], ignore_conflicts=True)