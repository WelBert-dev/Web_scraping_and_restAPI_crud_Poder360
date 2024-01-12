from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from .scrapers import ScraperUtil
from .validators import URLQueryStringParameterValidator

from trigger_web_scraping_dou_api.serializers import JournalJsonArrayOfDOUSerializer
from trigger_web_scraping_dou_api.models import JournalJsonArrayOfDOU

import os

DOU_BASE_URL=os.getenv('DOU_BASE_URL', 'https://www.in.gov.br/leiturajornal') 

class ScraperViewSet(APIView):
    def get(self, request):
        secaoURLQueryString = request.GET.get('secao')
        dataURLQueryString = request.GET.get('data')
        
        saveInDBFlagURLQueryString = request.GET.get('saveInDBFlag')


        # Se não existem parâmetros
        if URLQueryStringParameterValidator.is_empty_params(secaoURLQueryString, dataURLQueryString):
            
            if saveInDBFlagURLQueryString:

                return Response(self.handle_URL_empty_params(saveInDBFlagURLQueryString=True))
            
            return Response(self.handle_URL_empty_params(saveInDBFlagURLQueryString=False))


        # Se ?section= foi passado no URL query string param
        elif URLQueryStringParameterValidator.is_secaoURLQueryString_unic(secaoURLQueryString, dataURLQueryString) and \
             URLQueryStringParameterValidator.is_secaoURLQueryString_valid(secaoURLQueryString):
            
            if saveInDBFlagURLQueryString:
                
                print("IF DO saveInDBFlagURLQueryString executado!!!!!!!!!")
                
                return Response(self.handle_secaoURLQueryString_single_param(secaoURLQueryString, saveInDBFlagURLQueryString=True))
            
            return Response(self.handle_secaoURLQueryString_single_param(secaoURLQueryString, saveInDBFlagURLQueryString=False))
        
        
        # Se ?data= foi passado no URL query string param
        elif (URLQueryStringParameterValidator.is_dataURLQueryString_unic(secaoURLQueryString, dataURLQueryString) and \
              URLQueryStringParameterValidator.is_dataURLQueryString_valid(dataURLQueryString)):
                 
            return Response(self.handle_dataURLQueryString_single_param(dataURLQueryString))
        
        
        # Se ?section= e ?data= foi passado no URL query string param
        elif (URLQueryStringParameterValidator.is_all_params(secaoURLQueryString, dataURLQueryString) and \
              URLQueryStringParameterValidator.is_all_params_valid(secaoURLQueryString, dataURLQueryString)):
                 
            return Response(self.handle_all_params(secaoURLQueryString, dataURLQueryString))
        
        
        return Response("Operação inválida, mais informações no /djangoapp/validators_log.txt")
    
    
    
        
    # --------------------- [ Handlers área ] ---------------------

    # Varre tudo da home do https://www.in.gov.br/leiturajornal
    # - GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/ 
    def handle_URL_empty_params(self, saveInDBFlagURLQueryString):
        
        return ScraperUtil.run_generic_scraper(DOU_BASE_URL, saveInDBFlagURLQueryString)
        

    # Varre os DOU da seção mencionada no query string param, na data atual
    # - GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?secao=`do1 | do2 | do3`
    def handle_secaoURLQueryString_single_param(self, secaoURLQueryString_param, saveInDBFlagURLQueryString):
        
        return ScraperUtil.run_scraper_with_section(DOU_BASE_URL, secaoURLQueryString_param, saveInDBFlagURLQueryString)
    
    
    # Varre todos os DOU da data mencionada no query string param
    # - GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?data=`DD-MM-AAAA`
    def handle_dataURLQueryString_single_param(self, dataURLQueryString):
        
        return ScraperUtil.run_scraper_with_date(DOU_BASE_URL, dataURLQueryString)
    
    
    # Varre os DOU da seção e data mencionada no query string param
    # - GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?secao=`do1 | do2 | do3`&data=`DD-MM-AAAA`
    def handle_all_params(self, secaoURLQueryString, dataURLQueryString):
        
        return ScraperUtil.run_scraper_with_all_params(DOU_BASE_URL, secaoURLQueryString, dataURLQueryString)





class JournalJsonArrayOfDOUViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows JsonArrayOfDOU to be viewed or edited.
    """
    queryset = JournalJsonArrayOfDOU.objects.all()
    serializer_class = JournalJsonArrayOfDOUSerializer