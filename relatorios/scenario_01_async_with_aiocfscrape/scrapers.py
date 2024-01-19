import json
import cfscrape
from bs4 import BeautifulSoup

import os

import logging

import asyncio

from concurrent.futures import ProcessPoolExecutor

from aiocfscrape import CloudflareScraper

log_path = os.path.join(os.environ.get('LOG_DIR', '.'), 'scrapers_api2_djangoappclonetwo_log.txt')

logging.basicConfig(filename=log_path, level=logging.ERROR,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


DOU_BASE_URL=os.getenv('DOU_BASE_URL', 'https://www.in.gov.br/leiturajornal') 
DOU_DETAIL_SINGLE_RECORD_URL=os.getenv('DOU_DETAIL_SINGLE_RECORD_URL', 'https://www.in.gov.br/en/web/dou/-/') 


class ScraperUtil:
    
    logger = logging.getLogger("ScraperUtil")
    
    @staticmethod
    async def make_request_cloudflare_bypass_async_with_aiocfscrape(url):
        async with CloudflareScraper() as session:
            async with session.get(url) as resp:
                return await resp.text()
 
        
    
    @staticmethod
    def run_scraper_with_all_params(secaoURLQueryString_param : str, 
                                    dataURLQueryString_param : str, detailDOUJournalFlag : bool):
        
        # Varre todos os DOU da data mencionada no query string param
            
        url_param = DOU_BASE_URL + "?data=" + dataURLQueryString_param + "&secao=" + secaoURLQueryString_param
        
        dou_dontDetails_list_with_jsonArrayField = ScraperUtil.run_dontDetailsPage_scraper(url_param)
        
        if detailDOUJournalFlag:
            
            # Detalhar compensa async, pois são várias requisições para serem realizadas ao mesmo tempo.
            
            return ScraperUtil.run_detailsPage_scraper_using_async(dou_dontDetails_list_with_jsonArrayField)
        
        return dou_dontDetails_list_with_jsonArrayField

    
    
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
    def run_detailsPage_scraper_using_async(dou_dontDetails_list_with_jsonArrayField):
       
        urls_title_list = []
        for single_journal in dou_dontDetails_list_with_jsonArrayField:
            for record in single_journal:
                if record["urlTitle"] is not None:
                     urls_title_list.append(record["urlTitle"])
        
        return ScraperUtil.run_detail_single_dou_record_scraper_using_event_loop(urls_title_list)
    
    
    
    @staticmethod
    async def run_beautifulSoup_into_detailsPage_async(response):
        
        site_html_str = BeautifulSoup(response, "html.parser")

            
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
    async def make_request_to_dou_journal_moreDetail_and_scraping_async_task(url_tile):
        try:
            
            url_param = DOU_DETAIL_SINGLE_RECORD_URL + url_tile
            response = await ScraperUtil.make_request_cloudflare_bypass_async_with_aiocfscrape(url_param)
    
            result_json = await ScraperUtil.run_beautifulSoup_into_detailsPage_async(response)
        
            return result_json   
            
        except Exception as e:
            
            ScraperUtil.logger.error('make_request_to_dou_journal_moreDetail_and_scraping_async: Erro: ' + str(e))

            print(f"ERROR NA CHAMADA PARA: {url_tile}, {str(e)}")    
            
            # if str(e) == 'Cannot connect to host www.in.gov.br:443 ssl:default [Connection reset by peer]':
                
            return {'ERROR NA CHAMADA PARA': url_tile, 'Exception:':str(e)}
        
    
    
    # @staticmethod
    # async def make_request_to_dou_journal_moreDetail_and_scraping_async_again_when_error443(url_tile):
    #     try:
            
    #         url_param = DOU_DETAIL_SINGLE_RECORD_URL + url_tile
    #         response = await ScraperUtil.make_request_cloudflare_bypass_async(url_param)
    
    #         result_json = await ScraperUtil.run_beautifulSoup_into_detailsPage_async(response)
        
    #         return result_json   
            
    #     except Exception as e:
            
    #         ScraperUtil.logger.error('make_request_to_dou_journal_moreDetail_and_scraping_async: Erro: ' + str(e))

    #         print(f"ERROR NA CHAMADA PARA: {url_tile}, {str(e)}")    
            
    #         if str(e) == 'Cannot connect to host www.in.gov.br:443 ssl:default [Connection reset by peer]':
                
    #         return {'ERROR NA CHAMADA PARA': url_tile, 'Exception:':str(e)}
        


    @staticmethod
    async def run_detail_single_dou_record_scraper_async_batch(urls_title_list):
        tasks = [ScraperUtil.make_request_to_dou_journal_moreDetail_and_scraping_async_task(url_title) for url_title in urls_title_list]
        return await asyncio.gather(*tasks)



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
        