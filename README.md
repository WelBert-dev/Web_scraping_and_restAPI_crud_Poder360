## Web Scraping no Diário Oficial da União (Plataforma Imprensa Nacional com dados públicos do governo) e REST API para expor a coleta desses dados. 

### URL dos Não Detalhados: [https://www.in.gov.br/leiturajornal](https://www.in.gov.br/leiturajornal)
### URL dos Detalhados: [https://www.in.gov.br/en/web/dou/-/ + `urlTitle`](https://www.in.gov.br/en/web/dou/-/)

## Get Started

1. Instale o Docker:

```bash
$ apt install docker
$ apt install docker-compose
```

2. Clone o repositório:

```bash
$ git clone https://github.com/WelBert-dev/web_scraping_and_restAPI_crud_Poder360.git
$ cd ./web_scraping_and_restAPI_crud_Poder360
```

3. Execute a aplicação:

```bash
$ docker-compose up --build
```

## Atualizações na Estrutura do Docker ou Erros de Montagem

Em caso de alterações na implementação que não refletem no Docker ou erros na montagem das camadas, execute os seguintes comandos para limpar o cache do Docker:

```bash
$ sudo rm -r ./data/
$ docker stop $(sudo docker ps -a -q) ; sudo docker system prune -f ; sudo docker rm -vf $(sudo docker ps -aq) ; sudo docker rmi -f $(sudo docker images -aq)
```

**Nota:** Este processo apagará todas as imagens Docker do sistema.


## Endpoints da API:

**Nota:** Sempre utilize `&saveInDBFlag=True`, pois esses enpoints são mais performáticos. Isso ocorre pois após finalizar a raspagem o cliente é redirecionado para o endpoint que faz a consulta para o banco de dados e retorna o json com paginação, desta forma não sobrecarrega a renderização do DOM (se estiver consumindo a API pelo browser).

### Jornais Não Detalhados:

- Todas seções DO1, DO2 e DO3 do dia atual:
  ```bash
  GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?saveInDBFlag=True
  ```

- Por seção mencionada, do dia atual:
  ```bash
  GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?secao=do1&saveInDBFlag=True
  GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?secao=do2&saveInDBFlag=True
  GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?secao=do3&saveInDBFlag=True
  ```

- Todas seções DO1, DO2 e DO3, da data mencionada:
  ```bash
  GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?data=12-01-2024&saveInDBFlag=True
  ```

- Por data e seção mencionados:
  ```bash
  GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?secao=do1&data=12-01-2024&saveInDBFlag=True
  ```

- Requisição para o banco dos registros não detalhados:
  ```bash
  http://127.0.0.1:8000/db_dou_api/journaljsonarrayofdouviewset/
  ```

### Jornais Detalhados:

**Nota:** Obs: Mesmo aplicando lógicas de retentaivas quando falha a requisição no servidor do gov, as vezes menos de 10 elementos vem com valores nullos, mas basta fazer a mesma requisição novamente que preenche + elementos, fique tranquilo pois o sistema não insere duplicatas ou valores NULL!! Vou implementar uma lógica de retentativa mais robusta. Mas já esta usável rsrs.. ;D 

**Nota:** Isso ocorre por servidores desativados, timeout, ou falhas no bypass do cloudflare (por conta da camada async adicionada no cfscrape que não é async), implementar lógica de retentativa sem condições de break pode cair em looping eterno.

- Todas seções DO1, DO2 e DO3 do dia atual:
  ```bash
  GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?detailDOUJournalFlag=True&saveInDBFlag=True
  ```

- Por seção mencionada, do dia atual:
  ```bash
  GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?secao=do1&detailDOUJournalFlag=True&saveInDBFlag=True
  GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?secao=do2&detailDOUJournalFlag=True&saveInDBFlag=True
  GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?secao=do3&detailDOUJournalFlag=True&saveInDBFlag=True
  ```

- Todas seções DO1, DO2 e DO3, da data mencionada:
  ```bash
  GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?data=12-01-2024&detailDOUJournalFlag=True&saveInDBFlag=true
  ```

- Por data e seção mencionados:
  ```bash
  GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?secao=do1&data=12-01-2024&detailDOUJournalFlag=True&saveInDBFlag=True
  ```

- Requisição para o banco dos registros detalhados:
  ```bash
  http://127.0.0.1:8000/db_dou_api/detailsinglejournalofdouviewset/
  ```
```

### Detalhes de cada registro (jornal) consulta INDIVIDUAL: 

- Detalhando um único registro (jornal) com o field URL TITLE:

  ```bash
  GET http://127.0.0.1:8000/trigger_web_scraping_dou_api/?detailSingleDOUJournalWithUrlTitleField=acordao-cofen-n-103-de-27-de-setembro-de-2022-459835961
  ```

### **Nota:** Para mais detalhes de implementação, técnicas, bibliotecas e tecnologias, todo o passo a passo do desenvolvimento foi documentado em: [passo_a_passo_de_desenvolvimento.txt](https://github.com/WelBert-dev/web_scraping_and_restAPI_crud_Poder360/blob/main/passo_a_passo_de_desenvolvimento.txt)