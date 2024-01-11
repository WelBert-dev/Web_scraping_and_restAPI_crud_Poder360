from datetime import datetime, timedelta
import pytz

class URLQueryStringParameterValidator:
    
    @staticmethod
    def is_empty_params(secaoURLQueryString : str, dataURLQueryString : str):
        
        return ( secaoURLQueryString is None and dataURLQueryString is None )
    
    @staticmethod
    def is_secaoURLQueryString_unic(secaoURLQueryString : str, dataURLQueryString : str):
        
        return ( secaoURLQueryString is not None and dataURLQueryString is None )

    @staticmethod
    def is_secaoURLQueryString_valid(secaoURLQueryString : str):
        
         return ( (secaoURLQueryString != "") and \
                 (secaoURLQueryString == "do1" or \
                  secaoURLQueryString == "do2" or \
                  secaoURLQueryString == "do3") )
    
    @staticmethod
    def is_dataURLQueryString_unic(secaoURLQueryString : str, dataURLQueryString : str):
        
        return (dataURLQueryString is not None and secaoURLQueryString is None)
    
    @staticmethod
    def is_dataURLQueryString_valid(dataURLQueryString : str):
        
        return DateValidator.execute(dataURLQueryString)





class DateValidator:
    
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
            # Verificar se o ano está no intervalo razoável (por exemplo, 1900 a 2100)
            if 1900 <= date.year <= 2100:
                return True
            else:
                return False
        except ValueError:
            return False

    @staticmethod
    def is_not_future_date(date):
        current_datetime = datetime.now()
        return date <= current_datetime