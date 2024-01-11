from rest_framework.response import Response
from rest_framework.views import APIView
from .scrappers import ScraperUtil
from .validators import URLQueryStringParameterValidator

import os

DOU_BASE_URL=os.getenv('DOU_BASE_URL', 'https://www.in.gov.br/leiturajornal') 

class ScraperViewSet(APIView):
    def get(self, request):
        secaoURLQueryString = request.GET.get('secao')
        dataURLQueryString = request.GET.get('data')


        # Se não existem parâmetros
        if URLQueryStringParameterValidator.is_empty_params(secaoURLQueryString, dataURLQueryString):
            
            return Response(self.handle_URL_empty_params())

        # Se ?section= foi passado no URL query string param
        elif URLQueryStringParameterValidator.is_secaoURLQueryString_unic(secaoURLQueryString, dataURLQueryString) and \
             URLQueryStringParameterValidator.is_secaoURLQueryString_valid(secaoURLQueryString):
                 
            return Response(self.handle_secaoURLQueryString_single_param(secaoURLQueryString))
        
        # Se ?data= foi passado no URL query string param
        elif (URLQueryStringParameterValidator.is_dataURLQueryString_unic(secaoURLQueryString, dataURLQueryString) and \
              URLQueryStringParameterValidator.is_dataURLQueryString_valid(dataURLQueryString)):
                 
            return Response(self.handle_dataURLQueryString_single_param(dataURLQueryString))
        

        return Response("Nenhum jornal encontrado! ;-;")



    
    # --------------------- [ Handlers área ] ---------------------

    # Varre tudo da home do https://www.in.gov.br/leiturajornal
    # - GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/ 
    def handle_URL_empty_params(self):
       
        return ScraperUtil.run_generic_scraper(DOU_BASE_URL)
    


    # Varre os DOU da seção mencionada no query string param, na data atual
    # - GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?secao=`do1 | do2 | do3`
    def handle_secaoURLQueryString_single_param(self, secaoURLQueryString_param):
        
        return ScraperUtil.run_scraper_with_section(DOU_BASE_URL, secaoURLQueryString_param)
    
    
    # Varre todos os DOU da data mencionada no query string param
    # - GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?data=`DD-MM-AAAA`
    def handle_dataURLQueryString_single_param(self, dataURLQueryString):
        
        return ScraperUtil.run_scraper_with_date(DOU_BASE_URL, dataURLQueryString)
    




     