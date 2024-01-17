import os
import logging


log_path = os.path.join(os.environ.get('LOG_DIR', '.'), 'validators_log.txt')

# Configuração do logger com um formato mais detalhado
logging.basicConfig(filename=log_path, level=logging.ERROR,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class URLQueryStringParameterValidator:
    
    logger = logging.getLogger("URLQueryStringParameterValidator")


    @staticmethod
    def is_secaoURLQueryString_valid(secaoURLQueryString : str):
        
        valid_values = {"do1", "do2", "do3"}
        result = secaoURLQueryString != "" and secaoURLQueryString in valid_values
        
        if not result:
            URLQueryStringParameterValidator.logger.error('is_secaoURLQueryString_valid: Invalid secaoURLQueryString pois não existe o dou ' + secaoURLQueryString + '!')
        
        return result