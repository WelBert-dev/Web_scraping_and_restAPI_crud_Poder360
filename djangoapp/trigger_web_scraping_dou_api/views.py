from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import status

from .scrapers import ScraperUtil
from .validators import URLQueryStringParameterValidator

from trigger_web_scraping_dou_api.serializers import JournalJsonArrayOfDOUSerializer
from trigger_web_scraping_dou_api.models import JournalJsonArrayOfDOU

import os

from datetime import datetime, timedelta
import pytz

import json

DOU_BASE_URL=os.getenv('DOU_BASE_URL', 'https://www.in.gov.br/leiturajornal') 
DOU_DETAIL_SINGLE_RECORD_URL=os.getenv('DOU_DETAIL_SINGLE_RECORD_URL', 'https://www.in.gov.br/en/web/dou/-/') 

class ScraperViewSet(APIView):
    def get(self, request):
        secaoURLQueryString = request.GET.get('secao')
        dataURLQueryString = request.GET.get('data')
        
        saveInDBFlagURLQueryString = request.GET.get('saveInDBFlag')
        
        detailSingleDOUJournalWithUrlTitleFieldURLQueryString = request.GET.get('detailSingleDOUJournalWithUrlTitleField')

        detailDOUJournalFlag = request.GET.get('detailDOUJournalFlag')

        # Se não existem parâmetros
        if URLQueryStringParameterValidator.is_empty_params(secaoURLQueryString, 
                                                            dataURLQueryString, 
                                                            detailSingleDOUJournalWithUrlTitleFieldURLQueryString):
            
            if saveInDBFlagURLQueryString and detailDOUJournalFlag is None:
                
                return self.handle_URL_empty_params(saveInDBFlagURLQueryString=True, detailDOUJournalFlag=False)
            
            elif detailDOUJournalFlag and saveInDBFlagURLQueryString is None:
                
                return self.handle_URL_empty_params(saveInDBFlagURLQueryString=False, detailDOUJournalFlag=True)
            
            elif saveInDBFlagURLQueryString and detailDOUJournalFlag:
                
                return self.handle_URL_empty_params(saveInDBFlagURLQueryString=True, detailDOUJournalFlag=True)
            
            
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
            
            if saveInDBFlagURLQueryString:    
                 
                return self.handle_detailSingleDOUJournalWithUrlTitleFieldURLQueryString_param(detailSingleDOUJournalWithUrlTitleFieldURLQueryString, 
                                                                                               saveInDBFlagURLQueryString=True)
            
            return self.handle_detailSingleDOUJournalWithUrlTitleFieldURLQueryString_param(detailSingleDOUJournalWithUrlTitleFieldURLQueryString, 
                                                                                           saveInDBFlagURLQueryString=False)
        
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
    def handle_URL_empty_params(self, saveInDBFlagURLQueryString, detailDOUJournalFlag):
        
        
        # Nenhuma matéria postada no dia atual, pega o dia anterior... 
        # Ou seja, MOCK por enquanto...
        date_utc_now = datetime.utcnow()
        saopaulo_tz = pytz.timezone('America/Sao_Paulo')
        date_sp_now = date_utc_now.replace(tzinfo=pytz.utc).astimezone(saopaulo_tz)
        date_sp_now_minus_one_day = date_sp_now - timedelta(days=2)
        date_sp_now_minus_one_day_formated_db_pattern = date_sp_now_minus_one_day.strftime("%d-%m-%Y")

        # Modifica a URL para apontar para o dia anterior
        new_url = DOU_BASE_URL + "?data="+date_sp_now_minus_one_day_formated_db_pattern      
        
        print(new_url)
        
        response = ScraperUtil.run_generic_scraper(new_url, saveInDBFlagURLQueryString)
        
        if detailDOUJournalFlag:

            # Itera sobre cada objeto JSON na lista
            
            response_json_with_all = []
            
            for obj in response:
                # Tenta extrair o valor da chave 'urlTitle' e adicioná-lo à lista
                url_title = obj.get("urlTitle")
                if url_title is not None:
                    
                    response_json_with_all.append(ScraperUtil.run_detail_single_dou_record_scraper(DOU_DETAIL_SINGLE_RECORD_URL, url_title))
            
            print(response_json_with_all)
            
            return self.handle_response(response_json_with_all)
             
        
        return self.handle_response(response)

        
    # Varre os DOU da seção mencionada no query string param, na data atual
    # - GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?secao=`do1 | do2 | do3`
    def handle_secaoURLQueryString_single_param(self, secaoURLQueryString_param, saveInDBFlagURLQueryString):
        
        response = ScraperUtil.run_scraper_with_section(DOU_BASE_URL, secaoURLQueryString_param, saveInDBFlagURLQueryString)
        
        return self.handle_response(response)
    
    
    # Varre todos os DOU da data mencionada no query string param
    # - GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?data=`DD-MM-AAAA`
    def handle_dataURLQueryString_single_param(self, dataURLQueryString, saveInDBFlagURLQueryString):
        
        response = ScraperUtil.run_scraper_with_date(DOU_BASE_URL, dataURLQueryString, saveInDBFlagURLQueryString)
        
        return self.handle_response(response) 
    
    
    # Varre os DOU da seção e data mencionada no query string param
    # - GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?secao=`do1 | do2 | do3`&data=`DD-MM-AAAA`
    def handle_secaoURLQueryString_and_dataURLQueryString_params(self, secaoURLQueryString, dataURLQueryString, saveInDBFlagURLQueryString):
        
        response = ScraperUtil.run_scraper_with_all_params(DOU_BASE_URL, secaoURLQueryString, dataURLQueryString, saveInDBFlagURLQueryString)

        return self.handle_response(response)
    
    
    # Detalha o single record do DOU utilizando o urlTitle mencionado no query string param
    # - GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?secao=`do1 | do2 | do3`&data=`DD-MM-AAAA`
    def handle_detailSingleDOUJournalWithUrlTitleFieldURLQueryString_param(self, detailSingleDOUJournalWithUrlTitleFieldURLQueryString, saveInDBFlagURLQueryString):
        
        response = ScraperUtil.run_detail_single_dou_record_scraper(DOU_DETAIL_SINGLE_RECORD_URL, detailSingleDOUJournalWithUrlTitleFieldURLQueryString)
        
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
