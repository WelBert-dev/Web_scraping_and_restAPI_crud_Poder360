import json
import cfscrape
from bs4 import BeautifulSoup


class ScraperUtil:
    @staticmethod
    def run_scraper(url_param: str):

        scraper = cfscrape.create_scraper()

        response = scraper.get(url_param)

        if response.status_code == 200:
            
            site_html_str = BeautifulSoup(response.text, "html.parser")

            # with open('saida.txt', 'w', encoding='utf-8') as arquivo:
            #     arquivo.write(str(site_html_str))

            all_script_tag_with_contains_response_json =  site_html_str.find('script', {'id': 'params'})

            if all_script_tag_with_contains_response_json:

                script_tag_with_contains_response_json = all_script_tag_with_contains_response_json.contents[0]

                script_tag_with_contains_response_json = json.loads(script_tag_with_contains_response_json)

                # with open('saida_json.txt', 'w', encoding='utf-8') as arquivo:
                #     arquivo.write(str(params_data))

                jsonArrayField = script_tag_with_contains_response_json.get("jsonArray")

                return jsonArrayField
            else:
                print("Tag <script id='params'> não encontrada.\nView do DOU sofreu mudanças! ;-;")
                
                return "Tag <script id='params'> não encontrada.\nView do DOU sofreu mudanças! ;-;"

        else:
            print(f"Falha na requisição. Código de status: {response.status_code}")

            return "Falha na requisição. Código de status: " + response.status_code