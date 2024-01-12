import json
import cfscrape
from bs4 import BeautifulSoup

from trigger_web_scraping_dou_api.models import JournalJsonArrayOfDOU


from datetime import datetime, timedelta
import pytz


class ScraperUtil:
    
    @staticmethod
    def run_generic_scraper(url_param: str, saveInDBFlagURLQueryString : bool):
        
        scraper = cfscrape.create_scraper()
        response = scraper.get(url_param)

        if response.status_code == 200:
            
            site_html_str = BeautifulSoup(response.text, "html.parser")

            all_scriptTag_that_contains_journals_json =  site_html_str.find('script', {'id': 'params'})

            if all_scriptTag_that_contains_journals_json:

                scriptTag_that_contains_journals_json = all_scriptTag_that_contains_journals_json.contents[0]

                journals_json = json.loads(scriptTag_that_contains_journals_json)

                jsonArrayField = journals_json.get("jsonArray")

                if jsonArrayField:
                    
                    if saveInDBFlagURLQueryString:
                        
                        # jsonArrayField = data.get('json_array_data', []) 
                        jsonArrayFieldObjectsList = [JournalJsonArrayOfDOU(**item) for item in jsonArrayField]
                        
                        # Antes de chamar bulk_create, transformação nos dados normalizando no padrão YYYY-MM-DD
                        for ato in jsonArrayFieldObjectsList:
                            ato.pubDate = datetime.strptime(ato.pubDate, "%d/%m/%Y").strftime("%Y-%m-%d")
                            
                        JournalJsonArrayOfDOU.objects.bulk_create(jsonArrayFieldObjectsList)
                        
                    return jsonArrayField
                
                else:

                    # Nenhuma matéria postada no dia atual, pega o dia anterior.
                    # Função recursiva, que fica fazendo rollback do dia até encontrar dados:
                    ScraperUtil.scrape_previous_day()
            else:
                
                return "Tag <script id='params'> não encontrada.\nView do DOU sofreu mudanças! ;-;"

        else:
            
            return "Falha na requisição. Código de status: " + response.status_code
    
    
    
    @staticmethod
    def run_scraper_with_section(url_param: str, secaoURLQueryString_param):
        
        # Todos argumentos presentes, Varre os DOU da seção mencionada no query string param, na data atual

        date_utc_now = datetime.utcnow()
        saopaulo_tz = pytz.timezone('America/Sao_Paulo')
        date_sp_now = date_utc_now.replace(tzinfo=pytz.utc).astimezone(saopaulo_tz)
        date_sp_now_formated_db_pattern = date_sp_now.strftime("%d-%m-%Y")
        
        url_param = url_param + "?data=" + date_sp_now_formated_db_pattern + "&secao=" + secaoURLQueryString_param
        
        return ScraperUtil.run_generic_scraper(url_param, False)
    
    
    
    @staticmethod
    def run_scraper_with_date(url_param: str, dataURLQueryString_param):
        
        # Varre todos os DOU da data mencionada no query string param
            
        url_param = url_param + "?data=" + dataURLQueryString_param
        
        return ScraperUtil.run_generic_scraper(url_param, False)
    
    
    
    @staticmethod
    def run_scraper_with_all_params(url_param: str, secaoURLQueryString_param, dataURLQueryString_param):
        
        # Varre todos os DOU da data mencionada no query string param
            
        url_param = url_param + "?data=" + dataURLQueryString_param + "&secao=" + secaoURLQueryString_param
        
        return ScraperUtil.run_generic_scraper(url_param, False)
            


    @staticmethod
    def scrape_previous_day():
        # # Nenhuma matéria postada no dia atual, pega o dia anterior.
        # date_utc_now = datetime.utcnow()
        # saopaulo_tz = pytz.timezone('America/Sao_Paulo')
        # date_sp_now = date_utc_now.replace(tzinfo=pytz.utc).astimezone(saopaulo_tz)
        # date_sp_now_minus_one_day = date_sp_now - timedelta(days=1)
        # date_sp_now_minus_one_day_formated_db_pattern = date_sp_now_minus_one_day.strftime("%d-%m-%Y")

        # # Modifica a URL para apontar para o dia anterior
        # new_url = f"modificar_sua_url_aqui_para_apontar_para_{date_sp_now_minus_one_day_formated_db_pattern}"

        # # Chama a função run_generic_scraper novamente com a nova URL
        # return ScraperUtil.run_generic_scraper(new_url)
        
        return "Nenhum jornal postado neste dia!\nPegar dias anteriores recursivamente em desenvolvimento..."
    
