from datetime import datetime, timedelta
import pytz

import os
import logging


log_path = os.path.join(os.environ.get('LOG_DIR', '.'), 'validators_log.txt')

# Configuração do logger com um formato mais detalhado
logging.basicConfig(filename=log_path, level=logging.ERROR,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class URLQueryStringParameterValidator:
    
    logger = logging.getLogger("URLQueryStringParameterValidator")
    
    @staticmethod
    def is_empty_params(secaoURLQueryString : str, dataURLQueryString : str, detailSingleDOUJournalWithUrlTitleFieldURLQueryString : str):
        
        return ( secaoURLQueryString is None and dataURLQueryString is None and detailSingleDOUJournalWithUrlTitleFieldURLQueryString is None)
    
    # @staticmethod
    # def is_empty_params(*params):
        
    #     return all(param is None for param in params)
    
    
    @staticmethod
    def is_secaoURLQueryString_unic(secaoURLQueryString : str, dataURLQueryString : str):
        
        return ( secaoURLQueryString is not None and dataURLQueryString is None )


    @staticmethod
    def is_secaoURLQueryString_valid(secaoURLQueryString : str):
        
        valid_values = {"do1", "do2", "do3"}
        result = secaoURLQueryString != "" and secaoURLQueryString in valid_values
        
        if not result:
            URLQueryStringParameterValidator.logger.error('is_secaoURLQueryString_valid: Invalid secaoURLQueryString pois não existe o dou ' + secaoURLQueryString + '!')
        
        return result
    
    
    @staticmethod
    def is_dataURLQueryString_unic(secaoURLQueryString : str, dataURLQueryString : str):
        
        return (dataURLQueryString is not None and secaoURLQueryString is None)
    
    
    @staticmethod
    def is_dataURLQueryString_valid(dataURLQueryString : str):
        
        return DateValidator.execute(dataURLQueryString)
    
    
    @staticmethod
    def is_secaoURLQueryString_and_dataURLQueryString_params(secaoURLQueryString : str, dataURLQueryString : str):
        
        return ( secaoURLQueryString is not None and dataURLQueryString is not None )
    
    
    @staticmethod
    def is_secaoURLQueryString_and_dataURLQueryString_valid(secaoURLQueryString : str, dataURLQueryString : str):
        
        return URLQueryStringParameterValidator.is_secaoURLQueryString_valid(secaoURLQueryString) and \
               URLQueryStringParameterValidator.is_dataURLQueryString_valid(dataURLQueryString)
        

    @staticmethod
    def is_urlTitleOfSingleDOUJournalURLQueryString_unic(urlTitleOfSingleDOUJournalURLQueryString : str, secaoURLQueryString : str, dataURLQueryString : str):
        
        return ( urlTitleOfSingleDOUJournalURLQueryString is not None and (secaoURLQueryString is None and dataURLQueryString  is None ))
    
    
    @staticmethod
    def is_urlTitleOfSingleDOUJournalURLQueryString_valid(urlTitleOfSingleDOUJournalURLQueryString : str):
           
        return urlTitleOfSingleDOUJournalURLQueryString != "" and urlTitleOfSingleDOUJournalURLQueryString is not None        
               
               
               
class DateValidator:
    
    logger = logging.getLogger("DateValidator")
    
    @staticmethod
    def execute(date_str):
        try:
            date = datetime.strptime(date_str, '%d-%m-%Y')
            
            return DateValidator.is_valid_year(date) and \
                   DateValidator.is_not_future_date(date)
        
        except ValueError:
            return False

    @staticmethod
    def is_valid_year(date):
        try:
            result = 1900 <= date.year <= 2100
            if not result:
            
                DateValidator.logger.error('is_valid_year: Invalid year pois o ano da data ' + date + ' não está em um intervalo consistente!')
                
            return result
        
        except ValueError:
            
            DateValidator.logger.error('is_valid_year: Year value is not valid, e lançou um exception no processo!')
            
            return False

    @staticmethod
    def is_not_future_date(date):
        
        current_datetime = datetime.now()
        
        result = date <= current_datetime
        
        if not result:
            DateValidator.logger.error('is_not_future_date: date value is not valid, '+ str(date) +' ainda não chegou ooooh!')
        
        return result