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
        
        # Se não existem parâmetros
        # Lembrando que se trata dos parâmetros: secaoURLQueryString, dataURLQueryString e detailSingleDOUJournalWithUrlTitleFieldURLQueryString
        # NÃO se trata das flags: saveInDBFlagURLQueryString e detailDOUJournalFlag.
        # Essas flags modificam o comportamento desses handlers abaixo.

        # Se ?section= foi passado no URL query string param
        if URLQueryStringParameterValidator.is_secaoURLQueryString_valid(secaoURLQueryString):
            
            print("MAIS UM GET PARA: " + secaoURLQueryString)
                
            return self.handle_details_the_dou_with_secaoURLQueryString(secaoURLQueryString)
                                                                
        
    
        
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
    def handle_details_the_dou_with_secaoURLQueryString(self, secaoURLQueryString_param):
        
        response = ScraperUtil.run_scraper_with_section_and_details_the_dous(secaoURLQueryString_param)
    
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
