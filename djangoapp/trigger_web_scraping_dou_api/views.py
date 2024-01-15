from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import status

from .scrapers import ScraperUtil
from .validators import URLQueryStringParameterValidator

from trigger_web_scraping_dou_api.serializers import JournalJsonArrayOfDOUSerializer
from trigger_web_scraping_dou_api.models import JournalJsonArrayOfDOU

from datetime import datetime, timedelta
import pytz

class ScraperViewSet(APIView):
    def get(self, request):
        secaoURLQueryString = request.GET.get('secao')
        dataURLQueryString = request.GET.get('data')
        
        saveInDBFlagURLQueryString = request.GET.get('saveInDBFlag')
        
        detailSingleDOUJournalWithUrlTitleFieldURLQueryString = request.GET.get('detailSingleDOUJournalWithUrlTitleField')

        detailDOUJournalFlag = request.GET.get('detailDOUJournalFlag')

        # Se não existem parâmetros
        # Lembrando que se trata dos parâmetros: secaoURLQueryString, dataURLQueryString e detailSingleDOUJournalWithUrlTitleFieldURLQueryString
        # NÃO se trata das flags: saveInDBFlagURLQueryString e detailDOUJournalFlag.
        # Essas flags modificam o comportamento desses handlers abaixo.
        if URLQueryStringParameterValidator.is_empty_params(secaoURLQueryString, 
                                                            dataURLQueryString, 
                                                            detailSingleDOUJournalWithUrlTitleFieldURLQueryString):
            
            if saveInDBFlagURLQueryString and detailDOUJournalFlag is None:
                
                # Varre a home do DOU sem detalhar cada registro e SALVA no final
                
                return self.handle_URL_empty_params(saveInDBFlagURLQueryString=True, detailDOUJournalFlag=False)
            
            elif detailDOUJournalFlag and saveInDBFlagURLQueryString is None:
                
                # Varre a home do DOU e DETALHA cada registro e NÃO salva no final
                return self.handle_URL_empty_params(saveInDBFlagURLQueryString=False, detailDOUJournalFlag=True)
            
            elif saveInDBFlagURLQueryString and detailDOUJournalFlag:
                
                # Flags TODAS estão presentes, varre a home do DOU e DETALHA cada registro SALVANDO no final
                
                return self.handle_response({'error_in_our_server_side':'Funcionalidade não implementada por conta do volume de dados!! mas o get all sem detalhamento possue essa featured! ;D', 'BUT':'MASSS nada me empede de implementar essa funcionalidade ai com vocês rsrs... vamos solucionar problemas aplicando tecnologia juntos? ^^'})
            
            
            # Flags NÃO estão presentes, varre a home do DOU sem detalhar cada registro e NÃO salva no final
            return self.handle_URL_empty_params(saveInDBFlagURLQueryString=False, detailDOUJournalFlag=False)
            

        # Se ?section= foi passado no URL query string param
        elif URLQueryStringParameterValidator.is_secaoURLQueryString_unic(secaoURLQueryString, 
                                                                          dataURLQueryString) and \
             URLQueryStringParameterValidator.is_secaoURLQueryString_valid(secaoURLQueryString):
            
            if saveInDBFlagURLQueryString:
                
                return self.handle_secaoURLQueryString_single_param(secaoURLQueryString, 
                                                                    saveInDBFlagURLQueryString=True)
            
            return self.handle_secaoURLQueryString_single_param(secaoURLQueryString, 
                                                                saveInDBFlagURLQueryString=False)
        
        
        # Se ?data= foi passado no URL query string param
        elif (URLQueryStringParameterValidator.is_dataURLQueryString_unic(secaoURLQueryString, 
                                                                          dataURLQueryString) and \
              URLQueryStringParameterValidator.is_dataURLQueryString_valid(dataURLQueryString)):
            
            if saveInDBFlagURLQueryString:    
                 
                return self.handle_dataURLQueryString_single_param(dataURLQueryString, 
                                                                   saveInDBFlagURLQueryString=True)
            
            return self.handle_dataURLQueryString_single_param(dataURLQueryString, 
                                                               saveInDBFlagURLQueryString=False)
        
        
        # Se ?section= e ?data= foi passado no URL query string param
        elif (URLQueryStringParameterValidator.is_secaoURLQueryString_and_dataURLQueryString_params(secaoURLQueryString, 
                                                                                                    dataURLQueryString) and \
              URLQueryStringParameterValidator.is_secaoURLQueryString_and_dataURLQueryString_valid(secaoURLQueryString, 
                                                                                                      dataURLQueryString)):
            
            if saveInDBFlagURLQueryString:    
                 
                return self.handle_secaoURLQueryString_and_dataURLQueryString_params(secaoURLQueryString, dataURLQueryString, saveInDBFlagURLQueryString=True)
            
            return self.handle_secaoURLQueryString_and_dataURLQueryString_params(secaoURLQueryString, dataURLQueryString, saveInDBFlagURLQueryString=False)
        
        
        # Se ?detailSingleDOUJournalWithUrlTitleField= foi passado no URL query string param
        elif (URLQueryStringParameterValidator.is_urlTitleOfSingleDOUJournalURLQueryString_unic(detailSingleDOUJournalWithUrlTitleFieldURLQueryString, 
                                                                                                secaoURLQueryString, 
                                                                                                dataURLQueryString) and \
              URLQueryStringParameterValidator.is_urlTitleOfSingleDOUJournalURLQueryString_valid(detailSingleDOUJournalWithUrlTitleFieldURLQueryString)):
            
            return self.handle_detailSingleDOUJournalWithUrlTitleFieldURLQueryString_param(detailSingleDOUJournalWithUrlTitleFieldURLQueryString)
        
        return Response("Operação inválida, mais informações no /djangoapp/validators_log.txt")
    
    
    
        
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


    # Varre tudo da home do https://www.in.gov.br/leiturajornal
    # - GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/ 
    
    # Varre tudo da home do https://www.in.gov.br/leiturajornal e detalha todos dou do dia
    # - GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?detailDOUJournalFlag=True
    
    # Obs: POR ENQUANTO ESTA APLICANDO APENAS PARA A SEÇÂO DO1!
    # Pois quando não passa parâmetros na URL do portal do DOU trás apenas o do1... 
    # Para testes por enquanto vou manter assim, pois é mais rápido para raspagem, mas vou corrigir jaja
    def handle_URL_empty_params(self, saveInDBFlagURLQueryString, detailDOUJournalFlag):
        
        response = ScraperUtil.run_scraper_with_empty_params(saveInDBFlagURLQueryString, detailDOUJournalFlag)
        
        return self.handle_response(response)

        
    # Varre os DOU da seção mencionada no query string param, na data atual
    # - GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?secao=`do1 | do2 | do3`
    def handle_secaoURLQueryString_single_param(self, secaoURLQueryString_param, saveInDBFlagURLQueryString):
        
        response = ScraperUtil.run_scraper_with_section(secaoURLQueryString_param, saveInDBFlagURLQueryString)
        
        return self.handle_response(response)
    
    
    # Varre todos os DOU da data mencionada no query string param
    # - GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?data=`DD-MM-AAAA`
    def handle_dataURLQueryString_single_param(self, dataURLQueryString, saveInDBFlagURLQueryString):
        
        response = ScraperUtil.run_scraper_with_date(dataURLQueryString, saveInDBFlagURLQueryString)
        
        return self.handle_response(response) 
    
    
    # Varre os DOU da seção e data mencionada no query string param
    # - GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?secao=`do1 | do2 | do3`&data=`DD-MM-AAAA`
    def handle_secaoURLQueryString_and_dataURLQueryString_params(self, secaoURLQueryString, dataURLQueryString, saveInDBFlagURLQueryString):
        
        response = ScraperUtil.run_scraper_with_all_params(secaoURLQueryString, dataURLQueryString, saveInDBFlagURLQueryString)

        return self.handle_response(response)
    
    
    # Detalha o single record do DOU utilizando o urlTitle mencionado no query string param
    # - GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?secao=`do1 | do2 | do3`&data=`DD-MM-AAAA`
    def handle_detailSingleDOUJournalWithUrlTitleFieldURLQueryString_param(self, detailSingleDOUJournalWithUrlTitleFieldURLQueryString):
        
        response = ScraperUtil.run_detail_single_dou_record_scraper(detailSingleDOUJournalWithUrlTitleFieldURLQueryString)
        
        if 'error_in_dou_server_side' in response:
            
            return Response(response, status=status.HTTP_500_BAD_REQUEST)
        
        return Response(response)




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
