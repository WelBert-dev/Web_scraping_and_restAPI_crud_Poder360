from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import status

from .scrapers import ScraperUtil
from .validators import URLQueryStringParameterValidator

class ScraperViewSet(APIView):
    def get(self, request):
        
        secaoURLQueryString = request.GET.get('secao')
        dataURLQueryString = request.GET.get('data')
        
        detailDOUJournalFlag = request.GET.get('detailDOUJournalFlag')
        
        if detailDOUJournalFlag:
            detailDOUJournalFlag = True
        
        # Se ?section= e ?data= foi passado no URL query string param
        if (URLQueryStringParameterValidator.is_secaoURLQueryString_and_dataURLQueryString_params(secaoURLQueryString, 
                                                                                                    dataURLQueryString) and \
              URLQueryStringParameterValidator.is_secaoURLQueryString_and_dataURLQueryString_valid(secaoURLQueryString, 
                                                                                                      dataURLQueryString)):
            print("MAIS UM GET PARA, utilizando data e seção: " + secaoURLQueryString)
            
            return self.handle_secaoURLQueryString_and_dataURLQueryString_params(secaoURLQueryString, 
                                                                                dataURLQueryString, 
                                                                                detailDOUJournalFlag)
        
                                                                
        
    
        
    # --------------------- [ Handlers área ] ---------------------
    
    
    # Lida com as responses dos handlers abaixo, evitando repetição de cod
    def handle_response(self, response):

        if isinstance(response, dict):
        
            if 'error_in_our_server_side' in response:
                
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            
            elif 'jsonArray_isEmpty' in response:
                
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            
            elif 'error_in_dou_server_side' in response:
                
                return Response(response, status=status.HTTP_500_BAD_REQUEST)
        
        else:
            
            for i in response:
        
                if i == 'error_in_our_server_side':
                    
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)
                
                elif i == 'jsonArray_isEmpty':
                    
                    return Response(response, status=status.HTTP_404_NOT_FOUND)
                
                elif i == 'error_in_dou_server_side':
                    
                    return Response(response, status=status.HTTP_500_BAD_REQUEST)
        
        return Response(response)
        
        
    
    # Varre os DOU da seção e data mencionada no query string param
    # - GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?secao=`do1 | do2 | do3`&data=`DD-MM-AAAA`
    # E Detalha cada jornal
    def handle_secaoURLQueryString_and_dataURLQueryString_params(self, secaoURLQueryString : str, 
                                                                 dataURLQueryString : str, 
                                                                 detailDOUJournalFlag : bool):
        
        response = ScraperUtil.run_scraper_with_all_params(secaoURLQueryString, dataURLQueryString, detailDOUJournalFlag)

        return self.handle_response(response)
    

