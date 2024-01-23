from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import status

from django.shortcuts import redirect

import os

from .scrapers import ScraperUtil
from .validators import URLQueryStringParameterValidator

from trigger_web_scraping_dou_api.serializers import JournalJsonArrayOfDOUSerializer, DetailSingleJournalOfDOUSerializer
from trigger_web_scraping_dou_api.models import JournalJsonArrayOfDOU, DetailSingleJournalOfDOU
from trigger_web_scraping_dou_api.services import JournalJsonArrayOfDOUService, DetailSingleJournalOfDOUService


from concurrent.futures import ProcessPoolExecutor


# Esse endereço pode ser gerado de maneira dinâmica, quando está em ambiente de produção (local host)
# Ou quando esta em ambiente de produção (deploy), mas para nosso caso de uso já serve
# URL utilizada para redirecionar o cliente quando ele utiliza `saveInDBFlag=True`
# Pois a depender da quantidade de dados, quando não utilizar a flag de salvar, 
# toda a massa de dados é retornarda para o cliente, desta forma demora muito para renderizar o DOM

# Já a API do banco retorna os dados com paginação, assim não sobrecarrega o DOM.

URL_MAIN_API_DJANGOAPP=os.getenv('URL_MAIN_API_DJANGOAPP', 
                                    'http://127.0.0.1:8000/',) 

class ScraperViewSet(APIView):
    def get(self, request):
        secaoURLQueryString = request.GET.get('secao')
        dataURLQueryString = request.GET.get('data')
        
        saveInDBFlag = request.GET.get('saveInDBFlag')
        
        detailSingleDOUJournalWithUrlTitleFieldURLQueryString = request.GET.get('detailSingleDOUJournalWithUrlTitleField')

        detailDOUJournalFlag = request.GET.get('detailDOUJournalFlag')
        
        balancerFlag = request.GET.get('balancerFlag')
        
            
        if balancerFlag:
            balancerFlag = True
        
        if saveInDBFlag:
            saveInDBFlag = True
            
        if detailDOUJournalFlag:
            detailDOUJournalFlag = True
            


        # Se não existem parâmetros
        # Lembrando que se trata dos parâmetros: secaoURLQueryString, dataURLQueryString e detailSingleDOUJournalWithUrlTitleFieldURLQueryString
        # NÃO se trata das flags: saveInDBFlag e detailDOUJournalFlag.
        # Essas flags modificam o comportamento desses handlers abaixo.
        if URLQueryStringParameterValidator.is_empty_params(secaoURLQueryString, 
                                                            dataURLQueryString, 
                                                            detailSingleDOUJournalWithUrlTitleFieldURLQueryString):
            
            return self.handle_URL_empty_params(saveInDBFlag, detailDOUJournalFlag, balancerFlag)
             

        # Se ?section= foi passado no URL query string param
        elif URLQueryStringParameterValidator.is_secaoURLQueryString_unic(secaoURLQueryString, 
                                                                          dataURLQueryString) and \
             URLQueryStringParameterValidator.is_secaoURLQueryString_valid(secaoURLQueryString):
            
            return self.handle_secaoURLQueryString_single_param(secaoURLQueryString, 
                                                                saveInDBFlag, 
                                                                detailDOUJournalFlag)
        
        
        # Se ?data= foi passado no URL query string param
        elif (URLQueryStringParameterValidator.is_dataURLQueryString_unic(secaoURLQueryString, 
                                                                          dataURLQueryString) and \
              URLQueryStringParameterValidator.is_dataURLQueryString_valid(dataURLQueryString)):
            
            return self.handle_dataURLQueryString_single_param(dataURLQueryString, 
                                                               saveInDBFlag, 
                                                               detailDOUJournalFlag)
        
        
        # Se ?section= e ?data= foi passado no URL query string param
        elif (URLQueryStringParameterValidator.is_secaoURLQueryString_and_dataURLQueryString_params(secaoURLQueryString, 
                                                                                                    dataURLQueryString) and \
              URLQueryStringParameterValidator.is_secaoURLQueryString_and_dataURLQueryString_valid(secaoURLQueryString, 
                                                                                                      dataURLQueryString)):
            
            return self.handle_secaoURLQueryString_and_dataURLQueryString_params(secaoURLQueryString, 
                                                                                 dataURLQueryString, 
                                                                                 saveInDBFlag,
                                                                                 detailDOUJournalFlag)
        
        
        # Se ?detailSingleDOUJournalWithUrlTitleField= foi passado no URL query string param
        elif (URLQueryStringParameterValidator.is_urlTitleOfSingleDOUJournalURLQueryString_unic(detailSingleDOUJournalWithUrlTitleFieldURLQueryString, 
                                                                                                secaoURLQueryString, 
                                                                                                dataURLQueryString) and \
              URLQueryStringParameterValidator.is_urlTitleOfSingleDOUJournalURLQueryString_valid(detailSingleDOUJournalWithUrlTitleFieldURLQueryString)):
            
            return self.handle_detailSingleDOUJournalWithUrlTitleFieldURLQueryString_param(detailSingleDOUJournalWithUrlTitleFieldURLQueryString, 
                                                                                           saveInDBFlag, 
                                                                                           detailDOUJournalFlag)
        
        return Response("Operação inválida, mais informações no /djangoapp/validators_log.txt")
    
    
    
        
    # --------------------- [ Handlers área ] ---------------------
    
    
    # Lida com as responses dos handlers abaixo, evitando repetição de cod
    def handle_response_and_when_saveInDBFlag_is_true_save(self, response, 
                                                           saveInDBFlag : bool, 
                                                           detailDOUJournalFlag : bool):
        
        if isinstance(response, list):
            
            if saveInDBFlag:
                
                if detailDOUJournalFlag:
                    
                    print("DETAILS OBJECT SENDO INSERIDO NO BANCO....")
                    
                    with ProcessPoolExecutor() as executor:
    
                        executor.map(DetailSingleJournalOfDOUService.insert_into_distinct_journals_and_date_normalize, [response])
                
                    # Como salvou no banco, é melhor redirecionar para a rota da API que consulta a prórpia API do banco
                    # Pois a depender da quantidade de dados, quando não utilizar a flag de salvar, 
                    # toda a massa de dados é retornarda para o cliente, desta forma demora muito para renderizar o DOM
                    # Já a API do banco retorna os dados com paginação, assim não sobrecarrega o DOM.
                    return redirect(URL_MAIN_API_DJANGOAPP + 'db_dou_api/detailsinglejournalofdouviewset/')

                else:
                    
                    with ProcessPoolExecutor() as executor:
        
                        executor.map(JournalJsonArrayOfDOUService.insert_into_distinct_journals_and_date_normalize, [response])
                
                    # Como salvou no banco, é melhor redirecionar para a rota da API que consulta a prórpia API do banco
                    # Pois a depender da quantidade de dados, quando não utilizar a flag de salvar, 
                    # toda a massa de dados é retornarda para o cliente, desta forma demora muito para renderizar o DOM
                    # Já a API do banco retorna os dados com paginação, assim não sobrecarrega o DOM.
                    return redirect(URL_MAIN_API_DJANGOAPP + 'db_dou_api/journaljsonarrayofdouviewset/')

        elif isinstance(response, dict):
        
            if 'error_in_our_server_side' in response:
                
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            
            elif 'jsonArray_isEmpty' in response:
                
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            
            elif 'error_in_dou_server_side' in response:
                
                return Response(response, status=status.HTTP_500_BAD_REQUEST)
        
            elif saveInDBFlag:

                if detailDOUJournalFlag:
                    
                    print("DETAILS OBJECT SENDO INSERIDO NO BANCO....")

                else:
                    
                    with ProcessPoolExecutor() as executor:
        
                        executor.map(JournalJsonArrayOfDOUService.insert_into_distinct_journals_and_date_normalize, [response])
                
                    # Como salvou no banco, é melhor redirecionar para a rota da API que consulta a prórpia API do banco
                    # Pois a depender da quantidade de dados, quando não utilizar a flag de salvar, 
                    # toda a massa de dados é retornarda para o cliente, desta forma demora muito para renderizar o DOM
                    # Já a API do banco retorna os dados com paginação, assim não sobrecarrega o DOM.
                    return redirect(URL_MAIN_API_DJANGOAPP + 'db_dou_api/journaljsonarrayofdouviewset/')
            
        return Response(response)

    
    # Varre tudo da home do https://www.in.gov.br/leiturajornal
    # - GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/ 
    
    # Varre tudo da home do https://www.in.gov.br/leiturajornal e detalha todos dou do dia
    # - GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?detailDOUJournalFlag=True
    def handle_URL_empty_params(self, saveInDBFlag : bool, 
                                detailDOUJournalFlag : bool,
                                balancerFlag : bool):
        
        response = ScraperUtil.run_scraper_with_empty_params_using_clone_instances(detailDOUJournalFlag, balancerFlag)
        
        return self.handle_response_and_when_saveInDBFlag_is_true_save(response, saveInDBFlag, detailDOUJournalFlag)

        
    # Varre os DOU da seção mencionada no query string param, na data atual
    # - GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?secao=`do1 | do2 | do3`
    def handle_secaoURLQueryString_single_param(self, secaoURLQueryString_param : str, 
                                                saveInDBFlag : bool, 
                                                detailDOUJournalFlag : bool):
        
        response = ScraperUtil.run_scraper_with_section(secaoURLQueryString_param, 
                                                        detailDOUJournalFlag)
        
        return self.handle_response_and_when_saveInDBFlag_is_true_save(response, saveInDBFlag, detailDOUJournalFlag)
    
    
    # Varre todos os DOU da data mencionada no query string param
    # - GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?data=`DD-MM-AAAA`
    def handle_dataURLQueryString_single_param(self, dataURLQueryString: str, 
                                               saveInDBFlag : bool, 
                                               detailDOUJournalFlag : bool):
        
        response = ScraperUtil.run_scraper_with_date(dataURLQueryString, detailDOUJournalFlag)
        
        return self.handle_response_and_when_saveInDBFlag_is_true_save(response, saveInDBFlag, detailDOUJournalFlag) 
    
    
    # Varre os DOU da seção e data mencionada no query string param
    # - GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?secao=`do1 | do2 | do3`&data=`DD-MM-AAAA`
    def handle_secaoURLQueryString_and_dataURLQueryString_params(self, secaoURLQueryString : str, 
                                                                dataURLQueryString : str, 
                                                                saveInDBFlag : bool, 
                                                                detailDOUJournalFlag):
        
        response = ScraperUtil.run_scraper_with_all_params(secaoURLQueryString, dataURLQueryString, detailDOUJournalFlag)

        return self.handle_response_and_when_saveInDBFlag_is_true_save(response, saveInDBFlag, detailDOUJournalFlag)
    
    
    # Detalha o single record do DOU utilizando o urlTitle mencionado no query string param
    # - GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?secao=`do1 | do2 | do3`&data=`DD-MM-AAAA`
    def handle_detailSingleDOUJournalWithUrlTitleFieldURLQueryString_param(self, detailSingleDOUJournalWithUrlTitleFieldURLQueryString, saveInDBFlag, detailDOUJournalFlag):
        
        response = ScraperUtil.run_detail_single_dou_record_scraper(detailSingleDOUJournalWithUrlTitleFieldURLQueryString)
        
        return self.handle_response_and_when_saveInDBFlag_is_true_save(response, saveInDBFlag, detailDOUJournalFlag)




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
    
    
    
# ENDPOINT PARA A BASE DE DADOS LOCAL DOS JORNAIS DETALHADOS: 

# http://127.0.0.1:8000/db_dou_api/journaljsonarrayofdouviewset/?page=320

class DetailSingleJournalOfDOUViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows DetailSingleJournalOfDOU to be viewed or edited.
    """
    queryset = DetailSingleJournalOfDOU.objects.all()
    serializer_class = DetailSingleJournalOfDOUSerializer
