from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import status

from .scrapers import ScraperUtil
from .validators import URLQueryStringParameterValidator

from trigger_web_scraping_dou_api.serializers import JournalJsonArrayOfDOUSerializer
from trigger_web_scraping_dou_api.models import JournalJsonArrayOfDOU

class ScraperViewSet(APIView):
    def get(self, request):
        
        secaoURLQueryString = request.GET.get('secao')
        dataURLQueryString = request.GET.get('data')
        
        detailDOUJournalFlag = request.GET.get('detailDOUJournalFlag')
        
        
        # Se não existem parâmetros
        # Lembrando que se trata dos parâmetros: secaoURLQueryString, dataURLQueryString e detailSingleDOUJournalWithUrlTitleFieldURLQueryString
        # NÃO se trata das flags: saveInDBFlagURLQueryString e detailDOUJournalFlag.
        # Essas flags modificam o comportamento desses handlers abaixo.

        
        # Se ?section= foi passado no URL query string param
        if URLQueryStringParameterValidator.is_secaoURLQueryString_unic(secaoURLQueryString, 
                                                                          dataURLQueryString) and \
             URLQueryStringParameterValidator.is_secaoURLQueryString_valid(secaoURLQueryString):
                 
            print("MAIS UM GET PARA, utilizando seção: " + secaoURLQueryString)
                 
            if detailDOUJournalFlag:
                
                return self.handle_secaoURLQueryString_single_param_and_detail_the_dous(secaoURLQueryString)
            
            return self.handle_secaoURLQueryString_single_param(secaoURLQueryString)
        
        # Se ?section= e ?data= foi passado no URL query string param
        elif (URLQueryStringParameterValidator.is_secaoURLQueryString_and_dataURLQueryString_params(secaoURLQueryString, 
                                                                                                    dataURLQueryString) and \
              URLQueryStringParameterValidator.is_secaoURLQueryString_and_dataURLQueryString_valid(secaoURLQueryString, 
                                                                                                      dataURLQueryString)):
            print("MAIS UM GET PARA, utilizando data e seção: " + secaoURLQueryString)
            
            if detailDOUJournalFlag:
                
                return self.handle_secaoURLQueryString_and_dataURLQueryString_params_and_detail_the_dous(secaoURLQueryString, 
                                                                                                         dataURLQueryString)
            
            return self.handle_secaoURLQueryString_and_dataURLQueryString_params(secaoURLQueryString, 
                                                                                 dataURLQueryString)
                                                                
        
    
        
    # --------------------- [ Handlers área ] ---------------------
    
    
    # Lida com as responses dos handlers abaixo, evitando repetição de cod
    def handle_response(self, response):
        
        if 'error_in_our_server_side' in response:
            
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        elif 'jsonArray_isEmpty' in response:
            
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        
        elif 'error_in_dou_server_side' in response:
            
            return Response(response, status=status.HTTP_500_BAD_REQUEST)
        
        return Response(response)
        
    # Varre os DOU da seção mencionada no query string param, na data atual
    # - GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?secao=`do1 | do2 | do3`
    def handle_secaoURLQueryString_single_param(self, secaoURLQueryString_param):
        
        response = ScraperUtil.run_scraper_with_section(secaoURLQueryString_param)
    
        return self.handle_response(response)
    
    
    # Varre os DOU da seção mencionada no query string param, na data atual
    # - GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?secao=`do1 | do2 | do3`
    # E Detalha cada jornal
    def handle_secaoURLQueryString_single_param_and_detail_the_dous(self, secaoURLQueryString_param):
        
        response = ScraperUtil.run_scraper_with_section_and_detail_the_dou(secaoURLQueryString_param)
    
        return self.handle_response(response)
    
    
    # Varre os DOU da seção e data mencionada no query string param
    # - GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?secao=`do1 | do2 | do3`&data=`DD-MM-AAAA`
    def handle_secaoURLQueryString_and_dataURLQueryString_params_and_detail_the_dous(self, secaoURLQueryString, dataURLQueryString):
        
        response = ScraperUtil.run_scraper_with_all_params_and_detail_the_dou(secaoURLQueryString, dataURLQueryString)

        return self.handle_response(response)
    
    
    # Varre os DOU da seção e data mencionada no query string param
    # - GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?secao=`do1 | do2 | do3`&data=`DD-MM-AAAA`
    # E Detalha cada jornal
    def handle_secaoURLQueryString_and_dataURLQueryString_params(self, secaoURLQueryString, dataURLQueryString):
        
        response = ScraperUtil.run_scraper_with_all_params(secaoURLQueryString, dataURLQueryString)

        return self.handle_response(response)
    


# ENDPOINT PARA A BASE DE DADOS LOCAL DO jsonArray: 

# http://127.0.0.1:8000/db_dou_api/journaljsonarrayofdouviewset/?page=320

# Obtido no portal https://www.in.gov.br/leiturajornal:
# scriptTag = document.querySelectorAll("#params")[0]
# scriptTagTextContent = scriptTag.textContent 
# var jsonObj = JSON.parse(scriptTagTextContent);
class JournalJsonArrayOfDOUViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows JsonArrayOfDOU to be viewed or edited.
    """
    queryset = JournalJsonArrayOfDOU.objects.all()
    serializer_class = JournalJsonArrayOfDOUSerializer
