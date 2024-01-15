import json
import cfscrape
from bs4 import BeautifulSoup

import concurrent.futures

import os

from trigger_web_scraping_dou_api.services import JournalJsonArrayOfDOUService

from trigger_web_scraping_dou_api.utils import DateUtil


DOU_BASE_URL=os.getenv('DOU_BASE_URL', 'https://www.in.gov.br/leiturajornal') 
DOU_DETAIL_SINGLE_RECORD_URL=os.getenv('DOU_DETAIL_SINGLE_RECORD_URL', 'https://www.in.gov.br/en/web/dou/-/') 


class ScraperUtil:
    
    @staticmethod
    def run_parallel_process_generic_scraper(response, saveInDBFlagURLQueryString):
        
        site_html_str = BeautifulSoup(response.text, "html.parser")

        all_scriptTag_that_contains_dou_journals_json =  site_html_str.find('script', {'id': 'params'})
        
        if all_scriptTag_that_contains_dou_journals_json:

            scriptTag_that_contains_dou_journals_json = all_scriptTag_that_contains_dou_journals_json.contents[0]
            
            dou_journals_json = json.loads(scriptTag_that_contains_dou_journals_json)

            dou_journals_jsonArrayField_dict = dou_journals_json.get("jsonArray")

            if dou_journals_jsonArrayField_dict:
                
                if saveInDBFlagURLQueryString:
                    
                    with concurrent.futures.ProcessPoolExecutor() as executor:
    
                        executor.map(JournalJsonArrayOfDOUService.insert_into_distinct_with_dict, [dou_journals_jsonArrayField_dict])
                    
                return dou_journals_jsonArrayField_dict
            
            else:

                # Nenhuma matéria postada no dia atual, pega o dia anterior.
                # Função recursiva, que fica fazendo rollback do dia até encontrar dados:
                # ScraperUtil.scrape_previous_day()
                
                return ({"jsonArray_isEmpty":"objeto jsonArray é vazio, então não existem jornais para este dia!"})
            
        else:
            
            return ({"error_in_our_server_side":"Tag <script id='params'> não encontrada.\nView do DOU sofreu mudanças! ;-;"})
        
        
    
    @staticmethod
    def run_paralel_process_detail_single_dou_record_scraper(response):
        
        site_html_str = BeautifulSoup(response.text, "html.parser")

            
        versao_certificada = site_html_str.find('a', {'id': 'versao-certificada'})
        if versao_certificada:
            versao_certificada = versao_certificada.get('href')
            
        publicado_dou_data = site_html_str.find('span', {'class': 'publicado-dou-data'})
        if publicado_dou_data:
            publicado_dou_data = publicado_dou_data.text
        
        edicao_dou_data = site_html_str.find('span', {'class': 'edicao-dou-data'})
        if edicao_dou_data:
            edicao_dou_data = edicao_dou_data.text
            
        secao_dou_data = site_html_str.find('span', {'class': 'secao-dou-data'})
        if secao_dou_data:
            secao_dou_data = secao_dou_data.text
        
        orgao_dou_data = site_html_str.find('span', {'class': 'orgao-dou-data'})
        if orgao_dou_data:
            orgao_dou_data = orgao_dou_data.text
        
        title = site_html_str.find('p', {'class': 'identifica'})
        if title:
            title = title.text
        
        paragrafos = site_html_str.findAll('p', {'class': 'dou-paragraph'})
        paragraphs_list = []
        if paragrafos:
            for paragraph in paragrafos:
                if paragraph != "":
                    paragraphs_list.append(paragraph.text)
        
        assina = site_html_str.find('p', {'class': 'assina'})
        if assina:
            assina = assina.text

        # assina = site_html_str.findAll('span', {'class': 'assina'})
        cargo = site_html_str.find('p', {'class': 'cargo'})

        if cargo is None or not cargo or cargo == "":
            cargo = "Nenhum cargo identificado para este campo"
        
        else:
            cargo = cargo.text  
        
        return ({"versao_certificada":versao_certificada, 
                    "publicado_dou_data":publicado_dou_data,
                    "edicao_dou_data":edicao_dou_data,
                    "secao_dou_data":secao_dou_data,
                    "orgao_dou_data":orgao_dou_data,
                    "title":title,
                    "paragrafos":paragraphs_list,
                    "assina":assina,
                    "cargo":cargo})
        
        
        
    @staticmethod
    def run_generic_scraper(url_param: str, saveInDBFlagURLQueryString : bool):
        
        scraper = cfscrape.create_scraper()
        response = scraper.get(url_param)

        if response.status_code == 200:
            
            # Para processamentos em paralelo: ProcessPoolExecutor:
            # Para requisições network em paralelo ele é ruim, o melhor é o ThreadPoolExecutor
            with concurrent.futures.ProcessPoolExecutor() as executor:
                
                result = list(executor.map(ScraperUtil.run_parallel_process_generic_scraper, [response], [saveInDBFlagURLQueryString]))
        
            return result

        else:
            
            return ({"error_in_dou_server_side":response.text, "status_code":response.status_code, "response_obj":response})


        
    @staticmethod
    def run_detail_single_dou_record_scraper(detailSingleDOUJournalWithUrlTitleFieldURLQueryString):
        
        url_param = DOU_DETAIL_SINGLE_RECORD_URL + detailSingleDOUJournalWithUrlTitleFieldURLQueryString
        
        scraper = cfscrape.create_scraper()
        response = scraper.get(url_param)

        if response.status_code == 200:
            
            # Para processamentos em paralelo: ProcessPoolExecutor.
            # Para requisições network em paralelo ele é ruim, o melhor é o ThreadPoolExecutor
            with concurrent.futures.ProcessPoolExecutor() as executor:
                
                result = list(executor.map(ScraperUtil.run_paralel_process_detail_single_dou_record_scraper, [response]))
        
            return result

        else:
            
            return ({"error_in_dou_server_side":response.text, "status_code":response.status_code, "response_obj":response})
    
    
    
    @staticmethod
    def run_scraper_with_section(secaoURLQueryString_param, saveInDBFlagURLQueryString : bool):
        
        # Todos argumentos presentes, Varre os DOU da seção mencionada no query string param, na data atual
        
        date_now_db_and_brazilian_format = DateUtil.get_current_date_db_and_brazilian_format()
        
        url_param = DOU_BASE_URL + "?data=" + date_now_db_and_brazilian_format + "&secao=" + secaoURLQueryString_param
        
        return ScraperUtil.run_generic_scraper(url_param, saveInDBFlagURLQueryString)
    
    
    
    @staticmethod
    def run_scraper_with_date(dataURLQueryString_param, saveInDBFlagURLQueryString : bool):
        
        # Varre todos os DOU da data mencionada no query string param
        
        # OBS IMPORTANTE: Ao requisitar apenas a data na query string param, o padrão do portal https://www.in.gov.br/leiturajornal    
        # É retornar apenas o DOU1, então eu tive que implementar a lógica para requisitar os DOU2 e DOU3 
        # Na mão, ou seja, primeiro ele requisita o DOU1 + data, depois DOU2 + data ....
        
        
        # Palelelismo executando a função para cada elemento da lista: 
        dous_list = ['do1', 'do2', 'do3']
        with concurrent.futures.ThreadPoolExecutor() as executor:
           
            get_all_dous_with_current_date_dontDetails = list(executor.map(ScraperUtil.run_scraper_with_all_params, dous_list, [dataURLQueryString_param]*len(dous_list), [saveInDBFlagURLQueryString]*len(dous_list)))
            
        return get_all_dous_with_current_date_dontDetails
    
    
    
    @staticmethod
    def run_scraper_with_all_params(secaoURLQueryString_param, dataURLQueryString_param, saveInDBFlagURLQueryString : bool):
        
        # Varre todos os DOU da data mencionada no query string param
            
        url_param = DOU_BASE_URL + "?data=" + dataURLQueryString_param + "&secao=" + secaoURLQueryString_param
        
        return ScraperUtil.run_generic_scraper(url_param, saveInDBFlagURLQueryString)
    
    
    
    @staticmethod
    def run_scraper_with_empty_params(saveInDBFlagURLQueryString : bool, detailDOUJournalFlag : bool):
        
        date_now_db_and_brazilian_format = DateUtil.get_current_date_db_and_brazilian_format()
    
        # Palelelismo executando a função para cada elemento da lista: 
        dous_list = ['do1', 'do2', 'do3']
        with concurrent.futures.ThreadPoolExecutor() as executor:
           
            get_all_dous_with_current_date_dontDetails = list(executor.map(ScraperUtil.run_scraper_with_all_params, dous_list, [date_now_db_and_brazilian_format]*len(dous_list), [saveInDBFlagURLQueryString]*len(dous_list)))
        
        if detailDOUJournalFlag:
            
            urls_title_list = []
            for i in range(len(get_all_dous_with_current_date_dontDetails)): # Lista seção do1
                for j in range(len(get_all_dous_with_current_date_dontDetails[i])): # Lista seção do2  
                    for k in range(len(get_all_dous_with_current_date_dontDetails[i][j])): # Lista secão do3
                        
                        url_title = get_all_dous_with_current_date_dontDetails[i][j][k]["urlTitle"]
        
                        if url_title is not None:
                            urls_title_list.append(url_title)
                    
           # Palelelismo na raspagem do detalhamento para todos os dous também:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                
                get_all_dous_with_current_date_moreDetails = list(executor.map(ScraperUtil.run_detail_single_dou_record_scraper, urls_title_list))

            return get_all_dous_with_current_date_moreDetails

        return get_all_dous_with_current_date_dontDetails
 


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
