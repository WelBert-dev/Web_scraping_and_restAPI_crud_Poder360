import json
import cfscrape
from bs4 import BeautifulSoup

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

import os

import requests

import asyncio

from tenacity import retry

import logging

from itertools import chain

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


scraper = cfscrape.create_scraper()

# Exception apenas para o retry do tenacity capturar e re-executar novamente a requisição, até conseguir 100% dos resultados esperados...
# Condições de break não realizadas, correndo riscos de entrar em looping eterno caso o servidor do gov fique indisponível..
# Mas agora está retornando 100% dos resultados esperados!
class StatusCodeError(Exception):
    pass


class ScraperUtil:
    
    logger = logging.getLogger("ScraperUtil")
    
    @staticmethod
    @retry()
    async def make_request_cloudflare_bypass_async_multithreading(url):
      
        resp = await asyncio.to_thread(scraper.get, url, timeout=10)
    
        try:
            if resp.status_code != 200:
            
                print("STATUS CODE != 200 para: " + url)
                
                # Re-lança a exception para o retry capturar e executar novamente...
                # Em casos aonde o objeto response é existente, porém deu erro na resposta do gov side
                raise StatusCodeError("Erro para: "+ url +f"de status code: {resp.status_code}")
        except:
            
            # Re-lança a exception para o retry capturar e executar novamente...
            # Em casos aonde o objeto response é inexistente
            
            raise StatusCodeError("Erro para: "+ url +f"de status code: {resp.status_code}")
        return resp 
    
    @staticmethod
    def run_dontDetailsPage_scraper(url_param: str):
        
        
        response = scraper.get(url_param)

        if response.status_code == 200:
            
            # Para processamentos em paralelo: ProcessPoolExecutor:
            # Para requisições network em paralelo ele é ruim, o melhor é o ThreadPoolExecutor
            with ProcessPoolExecutor() as executor:
                
                result = list(executor.map(ScraperUtil.run_beautifulSoup_into_dontDetailsPage, [response]))
                
            return result

        else:
            
            ScraperUtil.logger.error('run_dontDetailsPage_scraper: Erro na requisição: , ' + response)
            
            return ({"error_in_dou_server_side":response.text, "status_code":response.status_code, "response_obj":response})



    @staticmethod
    def get_urlTitleField_from_dou_dontDetails_list_jsonArrayField(dou_dontDetails_list_with_jsonArrayField):
       
        urls_title_list = []
        for single_journal in dou_dontDetails_list_with_jsonArrayField:
            for record in single_journal:
                if record["urlTitle"] is not None:
                     urls_title_list.append(record["urlTitle"])
        
        return urls_title_list
    
    
    
    @staticmethod
    def run_detail_single_dou_record_scraper_using_event_loop(urls_title_list):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            all_dous_with_current_date_moreDetails = loop.run_until_complete(
                ScraperUtil.run_detail_single_dou_record_scraper_async_batch(urls_title_list)
            )
        finally:
            loop.close()

        return all_dous_with_current_date_moreDetails
    
    
    
    @staticmethod
    async def run_detail_single_dou_record_scraper_async_batch(urls_title_list):
        tasks = [ScraperUtil.make_request_to_dou_journal_moreDetail_and_scraping_async_task(url_title) for url_title in urls_title_list]
        return await asyncio.gather(*tasks)
    
    
    
    @staticmethod
    async def make_request_to_dou_journal_moreDetail_and_scraping_async_task(url_tile):
        try:
            
            url_param = DOU_DETAIL_SINGLE_RECORD_URL + url_tile
            response = await ScraperUtil.make_request_cloudflare_bypass_async_multithreading(url_param)
            
            print("Executando raspagem no: " + url_tile + "...")
    
            result_json = await ScraperUtil.run_beautifulSoup_into_detailsPage_async(response)
        
            return result_json   
            
        except Exception as e:
            
            ScraperUtil.logger.error('make_request_to_dou_journal_moreDetail_and_scraping_async: Erro: ' + str(e))

            print(f"ERROR NA CHAMADA PARA: {url_tile}, {str(e)}")    

    
    
    @staticmethod
    async def run_beautifulSoup_into_detailsPage_async(response):
        
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
        
        
        
    # Obs: Só utiliza este método quando é apenas uma requisição, no caso quando vai detalhar apenas um obj
    # Pois async só compensa quando existem mais de uma tarefa para ser realizada ao mesmo tempo
    # Pois quando é apenas uma tarefa, não surte efeitos utilizar async 
    # Uma vez que não vão existir 2 tarefas para serem executadas ao mesmo tempo 
    
    @staticmethod
    def run_detail_single_dou_record_scraper(detailSingleDOUJournalWithUrlTitleFieldURLQueryString):
        
        url_param = DOU_DETAIL_SINGLE_RECORD_URL + detailSingleDOUJournalWithUrlTitleFieldURLQueryString
    
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
    def run_scraper_with_section(secaoURLQueryString_param, detailDOUJournalFlag):
        
        # Todos argumentos presentes, Varre os DOU da seção mencionada no query string param, na data atual
        
        date_now_db_and_brazilian_format = DateUtil.get_current_date_db_and_brazilian_format()
        
        url_param = DOU_BASE_URL + "?data=" + date_now_db_and_brazilian_format + "&secao=" + secaoURLQueryString_param

        dou_dontDetails_list_with_jsonArrayField = ScraperUtil.run_dontDetailsPage_scraper(url_param)
        
        if detailDOUJournalFlag:
            
            urls_title_list = ScraperUtil.get_urlTitleField_from_dou_dontDetails_list_jsonArrayField(dou_dontDetails_list_with_jsonArrayField)

            return ScraperUtil.run_detail_single_dou_record_scraper_using_event_loop(urls_title_list)
        
        return dou_dontDetails_list_with_jsonArrayField
    
    
    
    @staticmethod
    def run_scraper_with_date(dataURLQueryString_param : str, detailDOUJournalFlag : bool):
        
        # Varre todos os DOU da data mencionada no query string param
        
        # OBS IMPORTANTE: Ao requisitar apenas a data na query string param, o padrão do portal https://www.in.gov.br/leiturajornal    
        # É retornar apenas o DOU1, então eu tive que implementar a lógica para requisitar os DOU2 e DOU3 
        # Na mão, ou seja, primeiro ele requisita o DOU1 + data, depois DOU2 + data ....
        
        
        # Palelelismo executando a função para cada elemento da lista: 
        # dous_list = ['do1', 'do2', 'do3']
        # with ThreadPoolExecutor() as executor:
           
        #     all_dous_with_current_date_dontDetails = list(executor.map(ScraperUtil.run_scraper_with_all_params, dous_list, [dataURLQueryString_param]*len(dous_list)))
            
        # return all_dous_with_current_date_dontDetails
        
        return ScraperUtil.run_scraper_using_clone_instances_when_secao_do1_do2_and_do3(dataURLQueryString_param, 
                                                                                        detailDOUJournalFlag,
                                                                                        balancerFlag=False)
    
    
    
    @staticmethod
    def run_scraper_with_all_params(secaoURLQueryString_param : str, 
                                    dataURLQueryString_param: str, detailDOUJournalFlag : bool):
        
        # Varre todos os DOU da data mencionada no query string param
        # Obs: Só usa async quando existem mais de uma requisição
        # Pois quando é apenas uma tarefa, não surte efeitos utilizar async 
        # Uma vez que não vão existir 2 tarefas para serem executadas ao mesmo tempo
            
        url_param = DOU_BASE_URL + "?data=" + dataURLQueryString_param + "&secao=" + secaoURLQueryString_param
        
        dou_dontDetails_list_with_jsonArrayField = ScraperUtil.run_dontDetailsPage_scraper(url_param)
        
        if detailDOUJournalFlag:
            
            # Detalhar compensa async, pois são várias requisições para serem realizadas ao mesmo tempo.
            
            urls_title_list = ScraperUtil.get_urlTitleField_from_dou_dontDetails_list_jsonArrayField(dou_dontDetails_list_with_jsonArrayField)

            return ScraperUtil.run_detail_single_dou_record_scraper_using_event_loop(urls_title_list)
        
        return dou_dontDetails_list_with_jsonArrayField
    
    
    
    @staticmethod        
    def run_scraper_with_empty_params_using_clone_instances(detailDOUJournalFlag : bool, balancerFlag : bool):
        
        date_now_db_and_brazilian_format = DateUtil.get_current_date_db_and_brazilian_format()
        
        return ScraperUtil.run_scraper_using_clone_instances_when_secao_do1_do2_and_do3(date_now_db_and_brazilian_format, 
                                                                                        detailDOUJournalFlag,
                                                                                        balancerFlag)
    
    
    
    @staticmethod        
    def run_scraper_using_clone_instances_when_secao_do1_do2_and_do3(dataURLQueryString_param : str, 
                                                                     detailDOUJournalFlag : bool, 
                                                                     balancerFlag : bool):
        
        # 127.0.0.1:8000/trigger_web_scraping_dou_api/?detailDOUJournalFlag=True&saveInDBFlag=True&balancerFlag=True
            
        # balancer e details true, executa raspagem dos dous não detalhados utilizando as 3 instâncias
        # depois, recebe a listagem e divide igualmente elas dinâmicamente para cada instância clone.
        # Envia no endpoint post com json contendo a lista de urlTitle para os detalhamentos de maneira distribuida
        
        # Com a flag `balancerFlag=True`, a instância vai executar a raspagem dos não detalhados,
        # e depois processar para retornar apenas a lista de urlTitle já pronta para 
            
        if detailDOUJournalFlag and balancerFlag:

            urls_clones_instances = [
                URL_API1_CLONE_INSTANCE_DJANGOAPPCLONEONE + 
                "trigger_web_scraping_dou_api/?secao=do1&data=" + dataURLQueryString_param +
                "&detailDOUJournalFlag=True" + "&balancerFlag=True",
                
                URL_API2_CLONE_INSTANCE_DJANGOAPPCLONETWO + 
                "trigger_web_scraping_dou_api/?secao=do2&data=" + dataURLQueryString_param + 
                "&detailDOUJournalFlag=True" + "&balancerFlag=True",
                
                URL_API3_CLONE_INSTANCE_DJANGOAPPCLONETHREE + 
                "trigger_web_scraping_dou_api/?secao=do3&data=" + dataURLQueryString_param + 
                "&detailDOUJournalFlag=True" + "&balancerFlag=True",
            ]      
        
            all_urlTitleList_response = ScraperUtil.run_make_get_request_for_others_clone_api_using_thread_pool(urls_clones_instances)
                
            # FAZ ACHATAMNETO DAS 3 listas, e transforma em apenas 1 com todsos os 3 dous:
            # Estilo `flatmap` dos fluxos Streams em Java.
                
            all_urlTitleList_response_flatList = list(chain.from_iterable(all_urlTitleList_response))
            
            # Particiona igualmente a quantidade de urlTitle para cada API realizar o detalhamento
            sublists = ScraperUtil.partition_list(all_urlTitleList_response_flatList, 3)
            
            # Manda um post com a lista de urlTitle dividida corretamente entre as 3 instâncias
            urls_clones_instances = [
                URL_API1_CLONE_INSTANCE_DJANGOAPPCLONEONE + 
                "trigger_web_scraping_dou_api/",
                
                URL_API2_CLONE_INSTANCE_DJANGOAPPCLONETWO + 
                "trigger_web_scraping_dou_api/",
                
                URL_API3_CLONE_INSTANCE_DJANGOAPPCLONETHREE + 
                "trigger_web_scraping_dou_api/",
            ] 
            return ScraperUtil.run_make_post_request_for_others_clone_api_using_thread_pool(urls_clones_instances, sublists)
            
        # 127.0.0.1:8000/trigger_web_scraping_dou_api/?saveInDBFlag=True
        elif not detailDOUJournalFlag: 
            
            urls_clones_instances = [
                URL_API1_CLONE_INSTANCE_DJANGOAPPCLONEONE + 
                "trigger_web_scraping_dou_api/?secao=do1&data=" + dataURLQueryString_param,
                
                URL_API2_CLONE_INSTANCE_DJANGOAPPCLONETWO + 
                "trigger_web_scraping_dou_api/?secao=do2&data=" + dataURLQueryString_param,
                
                URL_API3_CLONE_INSTANCE_DJANGOAPPCLONETHREE + 
                "trigger_web_scraping_dou_api/?secao=do3&data=" + dataURLQueryString_param,
            ]  
            
            return ScraperUtil.run_make_get_request_for_others_clone_api_using_thread_pool(urls_clones_instances)
        
        # 127.0.0.1:8000/trigger_web_scraping_dou_api/?detailDOUJournalFlag=True&saveInDBFlag=True
        elif not balancerFlag:
            
            urls_clones_instances = [
                URL_API1_CLONE_INSTANCE_DJANGOAPPCLONEONE + 
                "trigger_web_scraping_dou_api/?secao=do1&data=" + dataURLQueryString_param +
                "&detailDOUJournalFlag=True",
                
                URL_API2_CLONE_INSTANCE_DJANGOAPPCLONETWO + 
                "trigger_web_scraping_dou_api/?secao=do2&data=" + dataURLQueryString_param + 
                "&detailDOUJournalFlag=True",
                
                URL_API3_CLONE_INSTANCE_DJANGOAPPCLONETHREE + 
                "trigger_web_scraping_dou_api/?secao=do3&data=" + dataURLQueryString_param + 
                "&detailDOUJournalFlag=True",
            ]  
            return ScraperUtil.run_make_get_request_for_others_clone_api_using_thread_pool(urls_clones_instances)
        
    

    @staticmethod
    def make_get_request_for_others_clone_api_task(url):
        
        response = requests.get(url)

        try:
            
            if response.status_code == 200:
            
                return response.json()
            
            # 500 == Error no servidor do DOU
            elif response.status_code == 500:
                
                json_data = response.content.decode('utf-8')
                
                print("OCORREU ERROS NA REQUISIÇÃO DO DOU!")
                
                return json_data
            
                # raise Exception(f"Erro na requisição para {url}. Status code: {response.status_code}")
                
        except requests.exceptions.JSONDecodeError as e:
            
                json_string_response = json.dumps({"text": response})
            
                return json_string_response
            
            
            
    @staticmethod
    def make_post_request_for_others_clone_api_task(url_api, data):
        
         # Crie o corpo da solicitação como um dicionário
        corpo_json = {"urlTitleList": data}

        # Converta o dicionário para uma string JSON
        dados_json = json.dumps(corpo_json)

        # Defina os cabeçalhos necessários, por exemplo, 'Content-Type'
        cabecalhos = {"Content-Type": "application/json"}
               
        response = requests.post(url_api, data=dados_json, headers=cabecalhos)

        try:
            
            if response.status_code == 200:
            
                return response.json()
            
            # 500 == Error no servidor do DOU
            elif response.status_code == 500:
                
                json_data = response.content.decode('utf-8')
                
                print("OCORREU ERROS NA REQUISIÇÃO DO DOU!")
                
                return json_data
            
                # raise Exception(f"Erro na requisição para {url}. Status code: {response.status_code}")
                
        except requests.exceptions.JSONDecodeError as e:
            
                json_string_response = json.dumps({"text": response})
                
                return json_string_response
    
    
    
    @staticmethod
    def run_make_get_request_for_others_clone_api_using_thread_pool(urls_clones_instances):
        
        with ThreadPoolExecutor() as executor:
            all_urlTitleList_response = list(
                executor.map(
                    ScraperUtil.make_get_request_for_others_clone_api_task,
                    urls_clones_instances
                )
            )

        return all_urlTitleList_response
    
    
    
    @staticmethod
    def run_make_post_request_for_others_clone_api_using_thread_pool(urls_clones_instances, listas_particionadas):
        
        with ThreadPoolExecutor() as executor:
            all_urlTitleList_response = list(
                executor.map(
                    ScraperUtil.make_post_request_for_others_clone_api_task,
                    urls_clones_instances,
                    listas_particionadas
                )
            )

        return all_urlTitleList_response


    
    @staticmethod
    def partition_list(list, num_parts):
        
        part_size = -(-len(list) // num_parts)  # Arredondamento para cima
        partition_list = [list[i * part_size:(i + 1) * part_size] for i in range(num_parts)]
        return partition_list
    
    
    
    @staticmethod
    def run_beautifulSoup_into_dontDetailsPage(response):
        
        site_html_str = BeautifulSoup(response.text, "html.parser")
        all_scriptTag_that_contains_dou_journals =  site_html_str.find('script', {'id': 'params'})
        
        if all_scriptTag_that_contains_dou_journals:
            
            scriptTag_that_contains_dou_journals = all_scriptTag_that_contains_dou_journals.contents[0]

            dou_journals_json = json.loads(scriptTag_that_contains_dou_journals)

            dou_journals_jsonArrayField_dict = dou_journals_json.get("jsonArray")

            if dou_journals_jsonArrayField_dict:
            
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
    