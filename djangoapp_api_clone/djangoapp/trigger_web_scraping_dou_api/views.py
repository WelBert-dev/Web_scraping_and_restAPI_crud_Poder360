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
        
        # CODIGOS EM TESTE, FUNCIONANDO PARA GETALL MAS QUEBRA PARA OUTROS..
        # VOU PADRONIZAR AS RESPOSTAS DE TODOS ENDPOINTS PARA EVITAR PROBLEMAS DE SERIALIZAÇÃO
      
        # response_normalized = []
        # for i in response:

        #     if isinstance(i, dict): 
                
        #         # As vezes ocorrem erros em apenas alguns registros, por conta de certificado SSL,
        #         # Mas como só ocorre em ALGUNS, resolvi 
        #         if i.get('ERROR NA CHAMADA PARA'):
        #             print("\n\n\n")
        #             print("NOVO OBJ: ", i)
        #             print("\n\n\n")
        #             response_normalized.append({"versao_certificada": i['ERROR NA CHAMADA PARA'], 
        #                                             "publicado_dou_data": "",
        #                                             "edicao_dou_data":"",
        #                                             "secao_dou_data":"",
        #                                             "orgao_dou_data":"",
        #                                             "title":"",
        #                                             "paragrafos":"",
        #                                             "assina":"",
        #                                             "cargo":""})
                
        #         else:
                    
        #             response_normalized.append(i)

        # print("LEN DOS DOUS DETALHADOS: ", len(response_normalized))
        
        #  caminho_arquivo = "./usando_cfscrape_async_with_multithreading.txt"

        # # Abre o arquivo no modo de escrita
        # with open(caminho_arquivo, 'a') as arquivo:
        #     # Escreve cada objeto em uma nova linha
        #     for objeto in response:
        #         arquivo.write(str(objeto) + '\n')
        
        #  return Response(response_normalized, safe=False, status=status.HTTP_200_OK)
        
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
                    
                    

                    # if isinstance(i, dict): 
                        
                    #     # As vezes ocorrem erros em apenas alguns registros, por conta de certificado SSL,
                    #     # Mas como só ocorre em ALGUNS, resolvi 
                    #     if i.get('ERROR NA CHAMADA PARA'):
                    #         print("\n\n\n")
                    #         print("NOVO OBJ: ", i)
                    #         print("\n\n\n")
                    #         i = {"versao_certificada": i['ERROR NA CHAMADA PARA'], 
                    #              "publicado_dou_data": "",
                    #              "edicao_dou_data":"",
                    #              "secao_dou_data":"",
                    #              "orgao_dou_data":"",
                    #              "title":"",
                    #              "paragrafos":"",
                    #              "assina":"",
                    #              "cargo":""}
            
            return Response(response)
        
    
       
        
        
        
    
    # Varre os DOU da seção e data mencionada no query string param
    # - GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?secao=`do1 | do2 | do3`&data=`DD-MM-AAAA`
    # E Detalha cada jornal
    def handle_secaoURLQueryString_and_dataURLQueryString_params(self, secaoURLQueryString : str, 
                                                                 dataURLQueryString : str, 
                                                                 detailDOUJournalFlag : bool):
        
        response = ScraperUtil.run_scraper_with_all_params(secaoURLQueryString, dataURLQueryString, detailDOUJournalFlag)

        return self.handle_response(response)
    

