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
               