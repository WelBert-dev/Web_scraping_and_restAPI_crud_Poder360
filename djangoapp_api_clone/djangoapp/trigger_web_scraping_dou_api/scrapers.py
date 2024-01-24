import json
import cfscrape
from bs4 import BeautifulSoup

import os

import logging

import asyncio

from curl_cffi.requests import AsyncSession

from tenacity import retry

from concurrent.futures import ProcessPoolExecutor

log_path = os.path.join(os.environ.get('LOG_DIR', '.'), 'scrapers_api2_djangoappclonetwo_log.txt')

logging.basicConfig(filename=log_path, level=logging.ERROR,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


DOU_BASE_URL=os.getenv('DOU_BASE_URL', 'https://www.in.gov.br/leiturajornal') 
DOU_DETAIL_SINGLE_RECORD_URL=os.getenv('DOU_DETAIL_SINGLE_RECORD_URL', 'https://www.in.gov.br/en/web/dou/-/') 


# Exception apenas para o retry do tenacity capturar e re-executar novamente a requisição, até conseguir 100% dos resultados esperados...
# Condições de break não realizadas, correndo riscos de entrar em looping eterno caso o servidor do gov fique indisponível..
# Mas agora está retornando 100% dos resultados esperados!
class StatusCodeError(Exception):
    pass


# POR ENQUANTO UTILIZADO APENAS PELA FLAG DE BALANÇEAR CARGA `balancerFlag=True`
# Não removi ainda para realizar testes de performance com outras soluções
scraper = cfscrape.create_scraper() 

class ScraperUtil:
    
    logger = logging.getLogger("ScraperUtil")
    

    @staticmethod
    def run_scraper_with_all_params(secaoURLQueryString_param : str, 
                                    dataURLQueryString_param : str, detailDOUJournalFlag : bool, balancerFlag : bool):
        
        # Varre todos os DOU da data mencionada no query string param
            
        url_param = DOU_BASE_URL + "?data=" + dataURLQueryString_param + "&secao=" + secaoURLQueryString_param
        dou_dontDetails_list_with_jsonArrayField = ScraperUtil.run_dontDetailsPage_scraper(url_param)
        
        
        
        # Se for balancear entre os clones da API, faz a raspagem apenas na página dos não detalhados
        # Para posteriormente receber no endpoint POST http://127.0.0.1:800x/trigger_web_scraping_dou_api/
        # A listagem de urlTitle balanceada, ou seja, cada instância faz a mesma quantidade de requisições e 
        # raspagens dos jornais detalhados...
        if detailDOUJournalFlag and balancerFlag:
            
            return ScraperUtil.get_urlTitleField_from_dou_dontDetails_list_jsonArrayField(dou_dontDetails_list_with_jsonArrayField)
        
    
        
        # Detalhamentos sem balançear a carga, utilizando o `curl_cffi` no lugar do `cfscrape`
        # Pois ele é compilado em C, async e também possue funções para bypass nas restrições do cloudflare
        # Porém, é tão rápido que ocorrem bastante erros, e assim retentativas, mas mesmo assim ainda é mais rápido
        # Estou ajustando, e acredito que consigo resolver esse problema.
        
        elif detailDOUJournalFlag:
            
            urls_title_list = ScraperUtil.get_urlTitleField_from_dou_dontDetails_list_jsonArrayField(dou_dontDetails_list_with_jsonArrayField)
            
            # Executa todas as requisições primeiro e depois faz a raspagem se todos for 200 OK
            # Utilizando `curl_cffi`
            sites_list = asyncio.run(ScraperUtil.run_make_requests_to_detail_dou_journal_using_asyncio_gather_with_urlsTitleList(urls_title_list))

            
            # Verificações das urls que deu != 200 para retentativas até conseguir tudo
            # Enquanto status code != 200 realizamos requisições nas Fails Urls
            fails_urls_list = []
            success_sites_list = []
            while True:

                for site in sites_list:
                    if site.status_code != 200:
                        fails_urls_list.append(site.url)
                    else: 
                        success_sites_list.append(site)

                if len(fails_urls_list) == 0:
                    break
                
                sites_list = asyncio.run(ScraperUtil.run_retrying_make_requests_to_detail_dou_journal_using_asyncio_gather_with_urlsFailList(fails_urls_list))
                fails_urls_list = []
                
            return ScraperUtil.run_scraper_detail_dou_journal_using_event_loop(success_sites_list, urls_title_list)
        
        return list(dou_dontDetails_list_with_jsonArrayField)

    
    
    @staticmethod
    def run_dontDetailsPage_scraper(url_param: str):
        
        scraper = cfscrape.create_scraper()
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
         


    @staticmethod
    async def run_scraper_detail_dou_journal_async_task(site):
        try:
            # site[0] == html do site
            # site[1] == urlTitleField para fazer a animação no terminal
            print("Executando raspagem no: " + site[1])
            
            result_json = await ScraperUtil.run_beautifulSoup_into_detailsPage_async(site[0])
        
            return result_json   
            
        except Exception as e:
            
            ScraperUtil.logger.error('make_request_to_dou_journal_moreDetail_and_scraping_async: Erro: ' + str(e))

            print(f"ERROR NA CHAMADA PARA: {site[1]}, {str(e)}")    
        
        
    
    @staticmethod
    async def run_retrying_make_requests_to_detail_dou_journal_using_asyncio_gather_with_urlsFailList(urls_fail_list):

        async with AsyncSession() as s:
            tasks = []
            for url_fail in urls_fail_list:
                task = s.get(url_fail)  
                tasks.append(task)
            results = await asyncio.gather(*tasks)
        return results

    

    @staticmethod
    async def run_scraper_detail_dou_journal_async_batch(sites_lists, urls_title_list):

        task_pairs = list(zip(sites_lists, urls_title_list))
        
        tasks = [ScraperUtil.run_scraper_detail_dou_journal_async_task(site) for site in task_pairs]
            
        return await asyncio.gather(*tasks)
        


    @staticmethod
    async def run_make_requests_to_detail_dou_journal_using_asyncio_gather_with_urlsTitleList(urls_title_list):
        async with AsyncSession() as s:
            tasks = []
            try: 
                for url_title in urls_title_list:
                    url_param = DOU_DETAIL_SINGLE_RECORD_URL + url_title
                    task = s.get(url_param)
                    tasks.append(task)
                return await asyncio.gather(*tasks)
            
            except Exception as e:
                print(f"Erro durante a requisição: {url_title}, {e}")
                raise StatusCodeError("Erro para: "+ url_title +f"de status code: {task.status_code}")

    
    
    @staticmethod
    def run_scraper_detail_dou_journal_using_event_loop(sites_list, urls_title_list):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            all_dous_with_current_date_moreDetails = loop.run_until_complete(
                ScraperUtil.run_scraper_detail_dou_journal_async_batch(sites_list, urls_title_list)
            )
        finally:
            loop.close()

        return all_dous_with_current_date_moreDetails

    
    
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
        
      
    
    
    
    
    # Utilizados pela flag de balançear a carga `balancerFlag=True`, não removi ainda para realizar testes 
    # Até encontrar o melhor cenário para performance.
        
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

            print("Executando raspagem no: " + url_tile)
            
            result_json = await ScraperUtil.run_beautifulSoup_into_detailsPage_async(response)
        
            return result_json   
            
        except Exception as e:
            
            ScraperUtil.logger.error('make_request_to_dou_journal_moreDetail_and_scraping_async: Erro: ' + str(e))

            print(f"ERROR NA CHAMADA PARA: {url_tile}, {str(e)}")    
            


    @staticmethod
    @retry()
    async def make_request_cloudflare_bypass_async_multithreading(url):
      
        resp = await asyncio.to_thread(scraper.get, url, timeout=10)
    
        try:
            if resp.status_code != 200:
            
                print("STATUS CODE != 200 para: " + url)
                
                # Re-lança a exception para o retry capturar e executar novamente...
                # Em casos aonde o objeto response é existente, porém deu erro na resposta do gov side
                # Faz isso para que o retry capture e faça novas retentativas até conseguir 100% dos dados
                raise StatusCodeError("Erro para: "+ url +f"de status code: {resp.status_code}")
        except:
            
            # Re-lança a exception para o retry capturar e executar novamente...
            # Em casos aonde o objeto response é inexistente
            # Faz isso para que o retry capture e faça novas retentativas até conseguir 100% dos dados
            
            raise StatusCodeError("Erro para: "+ url +f"de status code: {resp.status_code}")
        
        return resp 

        