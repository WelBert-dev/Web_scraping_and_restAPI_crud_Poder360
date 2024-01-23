from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import status

import json

from .scrapers import ScraperUtil
from .validators import URLQueryStringParameterValidator

class ScraperViewSet(APIView):
    def get(self, request):
        
        secaoURLQueryString = request.GET.get('secao')
        dataURLQueryString = request.GET.get('data')
        
        detailDOUJournalFlag = request.GET.get('detailDOUJournalFlag')
        
        balancerFlag = request.GET.get('balancerFlag')
        
        
        
        if detailDOUJournalFlag:
            detailDOUJournalFlag = True
            
        if balancerFlag:
            balancerFlag = True
            
            
        # Se ?section= e ?data= foi passado no URL query string param
        if (URLQueryStringParameterValidator.is_secaoURLQueryString_and_dataURLQueryString_params(secaoURLQueryString, 
                                                                                                    dataURLQueryString) and \
              URLQueryStringParameterValidator.is_secaoURLQueryString_and_dataURLQueryString_valid(secaoURLQueryString, 
                                                                                                      dataURLQueryString)):
            print("MAIS UM GET PARA: " + secaoURLQueryString)
            
            return self.handle_balancer_secaoURLQueryString_and_dataURLQueryString_params(secaoURLQueryString, 
                                                                                dataURLQueryString, 
                                                                                detailDOUJournalFlag, 
                                                                                balancerFlag)
            
            
    # Utilizado para balancear as cargas de listas de url para raspagem,
    # recebe uma lista com a mesma quantidade de urls para cada instância da API:  
    # recebe apenas o field `urlTitle` na lista, faz a concatecanção com a DOU_DETAIL_SINGLE_RECORD_URL
    def post(self, request, *args, **kwargs):
        try:
            json_data = json.loads(request.body)
            
        except json.JSONDecodeError:
            return Response({'error': 'Dados JSON inválidos'}, status=400)
        
        data_json_list = json_data.get('urlTitleList', [])
        details_list = ScraperUtil.run_detail_single_dou_record_scraper_using_event_loop(data_json_list)


        return self.handle_response(details_list)
    
        
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
    def handle_balancer_secaoURLQueryString_and_dataURLQueryString_params(self, secaoURLQueryString : str, 
                                                                 dataURLQueryString : str, 
                                                                 detailDOUJournalFlag : bool,
                                                                 balancerFlag : bool):
        
        response = ScraperUtil.run_scraper_with_all_params(secaoURLQueryString, dataURLQueryString, detailDOUJournalFlag, balancerFlag)

        return self.handle_response(response)
    
