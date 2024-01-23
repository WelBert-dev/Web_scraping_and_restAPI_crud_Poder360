from datetime import datetime
from trigger_web_scraping_dou_api.models import JournalJsonArrayOfDOU, DetailSingleJournalOfDOU


class JournalJsonArrayOfDOUService:

    @staticmethod
    def insert_into_distinct_journals_and_date_normalize(dou_journals_jsonArrayField_dict):
        
        all_dous_records_normalized = []
        if len(dou_journals_jsonArrayField_dict) == 3: # Lista coontendo as 3 seções: DO1, DO2, e DO3
            
            # Acahat a lista em apenas uma, estilo "flatMap" dos fluxos streams no Java:
            dou_journals_jsonArrayField_dict = [item for sublist in dou_journals_jsonArrayField_dict for inner_list in sublist for item in inner_list]
            
            for record in dou_journals_jsonArrayField_dict:
                record['pubDate'] = datetime.strptime(record['pubDate'], "%d/%m/%Y").strftime("%Y-%m-%d")
                # Aproveita o mesmo looping para appender na lista se o objeto não existir no banco, 
                # para depois inserir tudo em massa na mesma query.
                all_dous_records_normalized.append(record)
        else:
            for record in dou_journals_jsonArrayField_dict: # Lista contendo apenas 1 dos DOU
                for i in record:
                    i['pubDate'] = datetime.strptime(i['pubDate'], "%d/%m/%Y").strftime("%Y-%m-%d")
                    # Aproveita o mesmo looping para appender na lista se o objeto não existir no banco, 
                    # para depois inserir tudo em massa na mesma query.
                    all_dous_records_normalized.append(i)
           
        # ignore_conflicts=True continua a inserir os objetos em cascata e quando encontra duplicatas não insere (ignora esse elemento) e continua operação..
        # Removi mais verificações para ganho de performance. (Desta forma esta resolvendo bem e não está duplicado, mais testes vão ser implementados no tests.py depois)
        JournalJsonArrayOfDOU.objects.bulk_create([JournalJsonArrayOfDOU(**item) for item in all_dous_records_normalized], ignore_conflicts=True)
                
                

class DetailSingleJournalOfDOUService:

    @staticmethod
    def insert_into_distinct_journals_and_date_normalize(details_dou_journals_dict):
            
        not_exists_records_list = []
        for record in details_dou_journals_dict:
        
            if isinstance(record, list): # Lista é para as 3 seções do dou.
                for i in record:
                    if i['publicado_dou_data'] and i['versao_certificada']:
                        i['publicado_dou_data'] = datetime.strptime(i['publicado_dou_data'], "%d/%m/%Y").strftime("%Y-%m-%d")
                        DetailSingleJournalOfDOUService.append_record_if_not_exists(i, not_exists_records_list)
                    else:
                        # OBEJETO NULL, CAÇANDO PROBLEMAS..
                        print("ANTENÇÃO, UM DOS OBJETOS A INSERIR ERA NULL, PROBLEMA SENDO RASTREADO... MAS OUTROS ESTÃO INTEGROS! ;D")

            elif isinstance(record, dict): # dict, é quando só foi solicitado uma das seções do dou.
                record['publicado_dou_data'] = datetime.strptime(record['publicado_dou_data'], "%d/%m/%Y").strftime("%Y-%m-%d")
                
                # Aproveita o mesmo looping para appender na lista se o objeto não existir no banco, 
                # para depois inserir tudo em massa na mesma query.
                DetailSingleJournalOfDOUService.append_record_if_not_exists(record, not_exists_records_list)
        
        
        # Utiliza a verificação CAMPO A CAMPO, pois apenas delegar para o ORM está inserindo duplicatas.
        # Devemos verificar tudo, pois não existe algum atributo que é UNICO para cad jornal, nem mesmo
        # a url da versão certificada (Pois essa URL se trata de uma página no jornal que contém mais registros)
   
        DetailSingleJournalOfDOU.objects.bulk_create([DetailSingleJournalOfDOU(**item) for item in not_exists_records_list], ignore_conflicts=True)       
            


    @staticmethod 
    def append_record_if_not_exists(single_journal_record, not_exists_records_list : list):
        
        if not DetailSingleJournalOfDOU.objects.filter(versao_certificada=single_journal_record['versao_certificada'], 
                                                    publicado_dou_data=single_journal_record['publicado_dou_data'],
                                                    edicao_dou_data=single_journal_record['edicao_dou_data'],
                                                    secao_dou_data=single_journal_record['secao_dou_data'],
                                                    orgao_dou_data=single_journal_record['orgao_dou_data'],
                                                    title=single_journal_record['title'],
                                                    paragrafos=single_journal_record['paragrafos'],
                                                    assina=single_journal_record['assina'],
                                                    cargo=single_journal_record['cargo']).exists():

                not_exists_records_list.append(single_journal_record)
                
                

            