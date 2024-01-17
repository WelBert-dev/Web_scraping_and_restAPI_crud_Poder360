import json
import cfscrape
from bs4 import BeautifulSoup

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

import os

import requests

import logging

from trigger_web_scraping_dou_api.services import JournalJsonArrayOfDOUService

from trigger_web_scraping_dou_api.utils import DateUtil

log_path = os.path.join(os.environ.get('LOG_DIR', '.'), 'scrapers_main_api_log.txt')

logging.basicConfig(filename=log_path, level=logging.ERROR,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


DOU_BASE_URL=os.getenv('DOU_BASE_URL', 'https://www.in.gov.br/leiturajornal') 
DOU_DETAIL_SINGLE_RECORD_URL=os.getenv('DOU_DETAIL_SINGLE_RECORD_URL', 'https://www.in.gov.br/en/web/dou/-/') 

URL_API1_CLONE_INSTANCE_DJANGOAPPCLONEONE=os.getenv('URL_API1_CLONE_INSTANCE_DJANGOAPPCLONEONE', 
                                                        'http://djangoappcloneone:8001/',) 

URL_API2_CLONE_INSTANCE_DJANGOAPPCLONETWO=os.getenv('URL_API2_CLONE_INSTANCE_DJANGOAPPCLONETWO',  
                                                         'http://djangoappclonetwo:8002/') 

URL_API3_CLONE_INSTANCE_DJANGOAPPCLONETHREE=os.getenv('URL_API3_CLONE_INSTANCE_DJANGOAPPCLONETHREE', 
                                                         'http://djangoappclonethree:8003/') 


class ScraperUtil:
    
    logger = logging.getLogger("ScraperUtil")
    
    @staticmethod
    def run_dontDetailsPage_scraper(url_param: str, saveInDBFlagURLQueryString : bool):
        
        scraper = cfscrape.create_scraper()
        response = scraper.get(url_param)

        if response.status_code == 200:
            
            # Para processamentos em paralelo: ProcessPoolExecutor:
            # Para requisições network em paralelo ele é ruim, o melhor é o ThreadPoolExecutor
            with ProcessPoolExecutor() as executor:
                
                result = list(executor.map(ScraperUtil.run_beautifulSoup_into_dontDetailsPage, [response], [saveInDBFlagURLQueryString]))
        
            return result

        else:
            
            ScraperUtil.logger.error('run_dontDetailsPage_scraper: Erro na requisição: , ' + response)
            
            return ({"error_in_dou_server_side":response.text, "status_code":response.status_code, "response_obj":response})


        
    @staticmethod
    def run_detail_single_dou_record_scraper(detailSingleDOUJournalWithUrlTitleFieldURLQueryString):
        
        url_param = DOU_DETAIL_SINGLE_RECORD_URL + detailSingleDOUJournalWithUrlTitleFieldURLQueryString
        
        scraper = cfscrape.create_scraper()
        response = scraper.get(url_param)

        if response.status_code == 200:
            
            # Para processamentos em paralelo: ProcessPoolExecutor.
            # Para requisições network em paralelo ele é ruim, o melhor é o ThreadPoolExecutor
            with ProcessPoolExecutor() as executor:
                
                result = list(executor.map(ScraperUtil.run_beautifulSoup_into_detailsPage, [response]))
        
            return result

        else:
            
            ScraperUtil.logger.error('run_detail_single_dou_record_scraper: Erro na requisição: , ' + response)
            
            return ({"error_in_dou_server_side":response.text, "status_code":response.status_code, "response_obj":response})
    
    
    
    @staticmethod
    def run_scraper_with_section(secaoURLQueryString_param, saveInDBFlagURLQueryString : bool):
        
        # Todos argumentos presentes, Varre os DOU da seção mencionada no query string param, na data atual
        
        date_now_db_and_brazilian_format = DateUtil.get_current_date_db_and_brazilian_format()
        
        url_param = DOU_BASE_URL + "?data=" + date_now_db_and_brazilian_format + "&secao=" + secaoURLQueryString_param
        
        return ScraperUtil.run_dontDetailsPage_scraper(url_param, saveInDBFlagURLQueryString)
    
    
    
    @staticmethod
    def run_scraper_with_date(dataURLQueryString_param, saveInDBFlagURLQueryString : bool):
        
        # Varre todos os DOU da data mencionada no query string param
        
        # OBS IMPORTANTE: Ao requisitar apenas a data na query string param, o padrão do portal https://www.in.gov.br/leiturajornal    
        # É retornar apenas o DOU1, então eu tive que implementar a lógica para requisitar os DOU2 e DOU3 
        # Na mão, ou seja, primeiro ele requisita o DOU1 + data, depois DOU2 + data ....
        
        
        # Palelelismo executando a função para cada elemento da lista: 
        dous_list = ['do1', 'do2', 'do3']
        with ThreadPoolExecutor() as executor:
           
            all_dous_with_current_date_dontDetails = list(executor.map(ScraperUtil.run_scraper_with_all_params, dous_list, [dataURLQueryString_param]*len(dous_list), [saveInDBFlagURLQueryString]*len(dous_list)))
            
        return all_dous_with_current_date_dontDetails
    
    
    
    @staticmethod
    def run_scraper_with_all_params(secaoURLQueryString_param, dataURLQueryString_param, saveInDBFlagURLQueryString : bool):
        
        # Varre todos os DOU da data mencionada no query string param
            
        url_param = DOU_BASE_URL + "?data=" + dataURLQueryString_param + "&secao=" + secaoURLQueryString_param
        
        return ScraperUtil.run_dontDetailsPage_scraper(url_param, saveInDBFlagURLQueryString)
    
    
    
    @staticmethod        
    def run_scraper_with_empty_params_using_others_instance_of_our_apis(saveInDBFlagURLQueryString : bool, detailDOUJournalFlag : bool):
        
        
        all_dous_with_current_date_dontDetails = []
        date_now_db_and_brazilian_format = DateUtil.get_current_date_db_and_brazilian_format()
        
        if not detailDOUJournalFlag: 
            
            # Não utiliza as instancias clones da API pois é mais rápido não detalhar cada jornal dou.
            dous_list = ['do1', 'do2', 'do3']
            all_dous_with_current_date_dontDetails = []
            with ThreadPoolExecutor() as executor:
            
                all_dous_with_current_date_dontDetails = executor.map(ScraperUtil.run_scraper_with_all_params, dous_list, [date_now_db_and_brazilian_format]*len(dous_list), [saveInDBFlagURLQueryString]*len(dous_list))
        
        else:
            
            # Utilizando as instancias clones da API em processo paralelo
            # urls_clones_instances = [
            # "http://djangoappcloneone:8001/trigger_web_scraping_dou_api/?secao=do1",
            # "http://djangoappclonetwo:8002/trigger_web_scraping_dou_api/?secao=do2",
            # "http://djangoappclonethree:8003/trigger_web_scraping_dou_api/?secao=do3",
            # ]
            
            urls_clones_instances = [
                URL_API1_CLONE_INSTANCE_DJANGOAPPCLONEONE + "trigger_web_scraping_dou_api/?secao=do1",
                URL_API2_CLONE_INSTANCE_DJANGOAPPCLONETWO + "trigger_web_scraping_dou_api/?secao=do2",
                URL_API3_CLONE_INSTANCE_DJANGOAPPCLONETHREE + "trigger_web_scraping_dou_api/?secao=do3",
            ]       
            
            all_dous_with_current_date_moreDetails = []
            
            # Pra cada um dos endpoints, execute em paralelo a chamada da função, iterando na lista, para cada elemento:
            # Delegando a responsabilidade de cada seção dou, para cada uma das instâncias...
            
            # Lá, vai ser executado o batch de urls com async (Foi a melhor configuração para este cenário)
            # Métricas no histórico do git.. rsrs
            
            with ThreadPoolExecutor() as executor:
            
                all_dous_with_current_date_moreDetails = list(executor.map(ScraperUtil.make_request_for_others_clone_api, urls_clones_instances))
            
            return all_dous_with_current_date_moreDetails
        
        return all_dous_with_current_date_dontDetails
    


    @staticmethod
    def make_request_for_others_clone_api(url):
        
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Erro na requisição para {url}. Status code: {response.status_code}")
    
    
    
    @staticmethod
    def run_beautifulSoup_into_dontDetailsPage(response, saveInDBFlagURLQueryString):
        
        site_html_str = BeautifulSoup(response.text, "html.parser")
        all_scriptTag_that_contains_dou_journals =  site_html_str.find('script', {'id': 'params'})
        
        if all_scriptTag_that_contains_dou_journals:
            
            scriptTag_that_contains_dou_journals = all_scriptTag_that_contains_dou_journals.contents[0]

            dou_journals_json = json.loads(scriptTag_that_contains_dou_journals)

            dou_journals_jsonArrayField_dict = dou_journals_json.get("jsonArray")

            if dou_journals_jsonArrayField_dict:
                
                if saveInDBFlagURLQueryString:
                    
                    with ProcessPoolExecutor() as executor:
    
                        executor.map(JournalJsonArrayOfDOUService.insert_into_distinct_journals_and_date_normalize, [dou_journals_jsonArrayField_dict])
                    
                return dou_journals_jsonArrayField_dict
            
            else:

                return ({"jsonArray_isEmpty":"objeto jsonArray é vazio, então não existem jornais para este dia!"})
            
        else:
            
            return ({"error_in_our_server_side":"Tag <script id='params'> não encontrada.\nView do DOU sofreu mudanças! ;-;"})
        
        
    
    @staticmethod
    def run_beautifulSoup_into_detailsPage(response):
        
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
        
