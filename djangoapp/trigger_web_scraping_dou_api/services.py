from datetime import datetime
from trigger_web_scraping_dou_api.models import JournalJsonArrayOfDOU

class JournalJsonArrayOfDOUService:

    @staticmethod
    def insert_into_distinct_with_dict(dou_journals_jsonArrayField_dict):
        
        url_titles_to_check = []
        for single_dou_journal_value in dou_journals_jsonArrayField_dict:
            # Normaliza a data no formato do db
            single_dou_journal_value['pubDate'] = datetime.strptime(single_dou_journal_value['pubDate'], "%d/%m/%Y").strftime("%Y-%m-%d")

        JournalJsonArrayOfDOU.objects.bulk_create([JournalJsonArrayOfDOU(**item) for item in dou_journals_jsonArrayField_dict], ignore_conflicts=True)