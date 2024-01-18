from datetime import datetime, timedelta
import pytz

class DateUtil:
    
    @staticmethod
    def get_current_date_db_and_brazilian_format():
        
        date_utc_now = datetime.utcnow()
        saopaulo_tz = pytz.timezone('America/Sao_Paulo')
        date_sp_now = date_utc_now.replace(tzinfo=pytz.utc).astimezone(saopaulo_tz)
        
        # date_sp_now = date_sp_now - timedelta(days=1)
        
        return date_sp_now.strftime("%d-%m-%Y")
