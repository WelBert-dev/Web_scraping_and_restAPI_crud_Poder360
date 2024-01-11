from rest_framework.response import Response
from rest_framework.views import APIView
from .utils import ScraperUtil

import os

DOU_BASE_URL=os.getenv('DOU_BASE_URL', 'https://www.in.gov.br/leiturajornal') 

class ScraperViewSet(APIView):
    def get(self, request):
        secaoURLQueryString = request.GET.get('secao')
        dataURLQueryString = request.GET.get('data')

        # Se não existem parâmetros
        if secaoURLQueryString is None and dataURLQueryString is None:
            return Response(self.handle_URL_empty_params())
    
        return Response({'mensagem': 'SEM RESULTADO'})

 
    # Varre tudo da home do https://www.in.gov.br/leiturajornal
    # - GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/ 
    def handle_URL_empty_params(self):
       
        return ScraperUtil.run_scraper(DOU_BASE_URL)




     