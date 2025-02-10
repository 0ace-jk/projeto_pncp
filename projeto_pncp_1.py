# ADIQUIRINDO DADOS DO PORTAL NACIONAL DE CONTRATAÇÕES PÚBLICAS

import pandas as pd
import re
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
# import openpyxl
import time
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

siglas_uf = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']

while True:
    data_inicial = input('Digite a data inicial no formato aaaaammdd: ')
    if len(data_inicial) != 8:
        print('Data informada está incorreta, voltando ao início \n\n')
        continue
    data_final = input('Digite a data final no formato aaaaammdd: ')
    if len(data_final) != 8:
        print('Data informada está incorreta, voltando ao início \n\n')
        continue
    question = input('Deseja expecificar a UF? (S/N)')
    if question.upper() == 'S':
        sigla_uf = input('Digite a sigla da UF: ')
        if sigla_uf.upper() in siglas_uf:
            sigla_uf = sigla_uf.upper()
        else:
            print('Sigla inválida, voltando ao início \n\n')
            sigla_uf = 0
            continue
    elif question.upper() == 'N':
        sigla_uf = 0
    else:
        print('Opção inválida, voltando ao início \n\n')
        sigla_uf = 0
        continue
    print(f'Data inicial: {data_inicial}')
    print(f'Data final: {data_final}')
    print(f'UF: {sigla_uf}')
    break

all_dfs = []

for id_contratacao in [6, 8, 9]:
    dfs = []
    if sigla_uf == 0:
        print(sigla_uf)
        url = (f'https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao?dataInicial={data_inicial}&dataFinal={data_final}&codigoModalidadeContratacao={id_contratacao}&pagina=1&tamanhoPagina=50')
    else:
        url = (f'https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao?dataInicial={data_inicial}&dataFinal={data_final}&codigoModalidadeContratacao={id_contratacao}&uf={sigla_uf}&pagina=1&tamanhoPagina=50')
    response = requests.get(url)
    if response.status_code == 200:
        total_paginas = pd.DataFrame(pd.read_json(url))['totalPaginas'][0]
        print(f'Página processada para id_contratacao {id_contratacao}, total de paginas: {total_paginas}')
        for pagina in range(1, total_paginas + 1):
            if sigla_uf == 0:
                url = (f'https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao?dataInicial={data_inicial}&dataFinal={data_final}&codigoModalidadeContratacao={id_contratacao}&pagina={pagina}&tamanhoPagina=50')
            elif sigla_uf != 0:
                url = (f'https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao?dataInicial={data_inicial}&dataFinal={data_final}&codigoModalidadeContratacao={id_contratacao}&uf={sigla_uf}&pagina={pagina}&tamanhoPagina=50')
            
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data']:
                    try:
                        df = pd.read_json(url).get('data')
                        if isinstance(df, list):
                          df = pd.DataFrame(df)
                        dfs.append(df)
                    except ValueError as e:
                        print(f"Erro processando id_contratacao {id_contratacao}, página {pagina}: {e}")
                else:
                    print(f"Sem dados para id_contratacao {id_contratacao}, página {pagina}")
            elif response.status_code == 204:
                print(f"Sem conteúdo para id_contratacao {id_contratacao}, página {pagina}. Skipping...")
                break
            else:
                print(f"erro para id_contratacao {id_contratacao}, página {pagina}: Status code {response.status_code}")

        if dfs:
            final_df = pd.concat(dfs, ignore_index=True)
            all_dfs.append(final_df)
        else:
            print(f"Sem df para concatenar para id_contratacao {id_contratacao}")
    elif response.status_code == 204:
        print(f"Sem conteúdo para id_contratacao {id_contratacao}. Pulando...")
    else:
        print(f"erro para id_contratacao {id_contratacao}: Status code {response.status_code}")

if all_dfs:
    final_df_all = pd.concat(all_dfs, ignore_index=True)
    print(final_df_all)
else:
    print("Sem dados para concatenar para todos id_contratacao.")

data_list = [x for x in final_df_all if isinstance(x, dict)]
dados = pd.DataFrame(data_list)

dados['uf_sigla'] = 0
dados['cidade_nome'] = 0
dados['unidade_nome'] = 0
dados['link_edital'] = 0

for x in dados.index:
    dados.loc[x, 'uf_sigla'] = dados['unidadeOrgao'][x]['ufSigla']
    dados.loc[x, 'cidade_nome'] = dados['unidadeOrgao'][x]['municipioNome']
    dados.loc[x, 'unidade_nome'] = dados['unidadeOrgao'][x]['nomeUnidade']
    dados.loc[x, 'link_edital'] = f'https://pncp.gov.br/app/editais/{dados.numeroControlePNCP[x].split('-')[0]+ '/' + dados.numeroControlePNCP[x][24:29] + '/' + dados.numeroControlePNCP[x][17:23]}'

colunas_remover = ['srp',
                   'usuarioNome',
                   'dataInclusao',
                   'dataPublicacaoPncp',
                   'orgaoEntidade',
                   'anoCompra',
                   'sequencialCompra',
                   'dataAtualizacao',
                   'numeroCompra',
                   'unidadeOrgao',
                   'amparoLegal',
                   'informacaoComplementar',
                   'processo',
                   'linkSistemaOrigem',
                   'justificativaPresencial',
                   'unidadeSubRogada',
                   'orgaoSubRogado',
                   'valorTotalHomologado',
                   'dataAtualizacaoGlobal',
                   'linkProcessoEletronico',
                   'modoDisputaId',
                   'modalidadeId',
                   'tipoInstrumentoConvocatorioNome',
                   'tipoInstrumentoConvocatorioCodigo',
                   'modoDisputaNome',
                   'situacaoCompraId',
                   'situacaoCompraNome',]

dados_limpos = dados.drop(columns=colunas_remover)

dados_limpos = dados_limpos.drop_duplicates(subset=['numeroControlePNCP'])

print(f'Quantitade de contratações analisadas: {dados_limpos.shape[0]}')

dados_limpos.to_csv(f'ph_{sigla_uf}_{data_inicial}_{data_final}.csv', index=False)

def replace_invalid_chars(text):

    ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]|[\xAD]')

    if isinstance(text, str):
        return ILLEGAL_CHARACTERS_RE.sub('', text)
    else:
        return text
    
for col in dados_limpos.select_dtypes(include=['object']).columns:
    dados_limpos[col] = dados_limpos[col].apply(replace_invalid_chars)

dados_limpos.to_excel(f'ph_{sigla_uf}_{data_inicial}_{data_final}.xlsx', index=False, engine='openpyxl')



# COLETA DE DADOS DOS ITENS

def check_exists_by_element(by, value):
    try:
        driver.find_element(by, value)
    except NoSuchElementException:
        return False
    return True


service = Service(r'C:\Users\chromedriver-win64\chromedriver.exe')
#### Importante colocar o caminho correto do chromedriver na variavel service ####

options = Options()
driver = webdriver.Chrome(service=service, options=options) 
delay = 10
driver.get('https://pncp.gov.br/app/editais?pagina=1')
time.sleep(5)

print('Criando DataFrame')
df = pd.DataFrame(columns=['n_item', 'objeto', 'qtd_total', 'valor_unitario', 'valor_total','modalidade_itens', 'link_edital', 'id_pncp', 'itens_edital', 'inicio_rec_proposta', 'fim_rec_proposta'])
df_itens_pncp = pd.DataFrame(columns=['n_item', 'objeto', 'qtd_total', 'valor_unitario', 'valor_total','modalidade_itens',  'link_edital', 'id_pncp', 'itens_edital', 'inicio_rec_proposta', 'fim_rec_proposta'])
b = 0
editais_erro = 0
erros_desconhecidos = []

print('Iniciando Loop')
for x in dados_limpos.numeroControlePNCP:
    url_pncp_itens = f'https://pncp.gov.br/app/editais/{x.split('-')[0]+ '/' + x[24:29] + '/' + x[17:23]}'
    b += 1
    driver.get(url_pncp_itens)
    print(f'Buscando edital {b} de: {dados_limpos.numeroControlePNCP.count()}')
    time.sleep(2)

    try:
        inicio_rec_proposta_lista = str(list(dados_limpos.dataAberturaProposta[dados_limpos.numeroControlePNCP == x]))[2:-2].replace('T', '-').split('-')
        inicio_rec_proposta = f'{inicio_rec_proposta_lista[2]}/{inicio_rec_proposta_lista[1]}/{inicio_rec_proposta_lista[0]} {inicio_rec_proposta_lista[3]}'
    except:
        print('erro1')
        inicio_rec_proposta = 0
        pass
    try:
        fim_rec_proposta_lista = str(list(dados_limpos.dataEncerramentoProposta[dados_limpos.numeroControlePNCP == x]))[2:-2].replace('T', '-').split('-')
        fim_rec_proposta = f'{fim_rec_proposta_lista[2]}/{fim_rec_proposta_lista[1]}/{fim_rec_proposta_lista[0]} {fim_rec_proposta_lista[3]}'
    except:
        print('erro2')
        fim_rec_proposta = 0
        pass
    id_pncp = x
    modalidade_itens = str(list(dados_limpos.modalidadeNome[dados_limpos.numeroControlePNCP == x])).replace("'", "").replace('[', '').replace(']', '')

    while True:
        if check_exists_by_element(By.TAG_NAME, 'pncp-select'):
            break
        else :
            print('Edital não carregado, tentando novamente')
            time.sleep(2)
            driver.get('https://pncp.gov.br/app/editais?pagina=1')
            time.sleep(4)
            driver.get(url_pncp_itens)
            time.sleep(6)
            break
            
    if check_exists_by_element(By.CLASS_NAME, 'content'):
        print('Edital em erro, buscando proximo edital')
        editais_erro += 1
        erros_desconhecidos.append(x)
        print('if 2')
        continue
    elif check_exists_by_element(By.TAG_NAME, 'pncp-select'):
        print('Edital carregado, continuando')
        pass
    else:
        print('Erro desconhecido, buscando proximo edital')
        editais_erro += 1
        erros_desconhecidos.append(x)
        continue


    iframe = driver.find_element(By.TAG_NAME, 'pncp-select')
    driver.execute_script('window.scrollTo(0, 0);')
    time.sleep(0.4)
    ActionChains(driver)\
        .scroll_to_element(iframe)\
        .perform()
    driver.find_element(By.TAG_NAME, 'pncp-select').click()
    time.sleep(0.2)
    driver.find_element(By.CLASS_NAME, 'ng-option.ng-star-inserted').click()
    time.sleep(0.2)

    df_temp = pd.DataFrame(columns=['n_item', 'objeto', 'qtd_total', 'valor_unitario', 'valor_total','modalidade_itens',  'link_edital', 'id_pncp', 'itens_edital', 'inicio_rec_proposta', 'fim_rec_proposta'])

    qtd_itens = driver.find_elements(By.CLASS_NAME, 'pagination-information.d-none.d-sm-flex')
    itens_edital = qtd_itens[0].text.split(' ')[-2]
    itens_pagina = (int(qtd_itens[0].text.split(' ')[-2]) - 0.1) / 50
    clicks_prox_pagina = int(str(itens_pagina).split('.')[0])
    print(f'Quantidade de itens nesse edital: {qtd_itens[0].text.split(' ')[-2]}')

    if clicks_prox_pagina >= 0:

        for a in range(clicks_prox_pagina+1):

            time.sleep(0.2)
            list2 = driver.find_elements(By.TAG_NAME, 'datatable-body-cell')
            df_temp = pd.DataFrame(columns=['n_item', 'objeto', 'qtd_total', 'valor_unitario', 'valor_total','modalidade_itens',  'link_edital', 'id_pncp', 'itens_edital', 'inicio_rec_proposta', 'fim_rec_proposta'])
            print(f'Buscando itens na página {a+1}. Edital {b} de: {dados_limpos.numeroControlePNCP.count()}')
            time.sleep(0.5)
            while True:
                if check_exists_by_element(By.ID, 'btn-next-page'):
                    break
                else:
                    print(f'Edital não carregado, tentando novamente. Edital {b} de: {dados_limpos.numeroControlePNCP.count()}')
                    time.sleep(5)
                    driver.refresh()
                    time.sleep(5)
                    
                continue

            for i in range(0,len(list2)-10, 6):
                n_item = list2[i].text
                objeto = list2[i+1].text
                qtd_total = list2[i+2].text
                valor_unitario = list2[i+3].text
                valor_total = list2[i+4].text
                link_edital = url_pncp_itens
                df_temp.loc[i] = [n_item, objeto, qtd_total, valor_unitario, valor_total,modalidade_itens, link_edital, id_pncp, itens_edital, inicio_rec_proposta, fim_rec_proposta]
            df_itens_pncp = pd.concat([df_itens_pncp, df_temp], ignore_index=True)
            time.sleep(0)

            if a < clicks_prox_pagina:
                driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)
                iframe = driver.find_element(By.ID, 'btn-next-page')
                ActionChains(driver)\
                    .scroll_to_element(iframe)\
                    .perform()
                time.sleep(0)                
                driver.find_element(By.ID, 'btn-next-page').click()
                time.sleep(0.4)
            else:
                print('S <3')
            print(f'Página {a+1} finalizada')

    elif clicks_prox_pagina == 0:

        list2 = driver.find_elements(By.TAG_NAME, 'datatable-body-cell')

        for i in range(0,len(list2)-10, 6):
            n_item = list2[i].text
            objeto = list2[i+1].text
            qtd_total = list2[i+2].text
            valor_unitario = list2[i+3].text
            valor_total = list2[i+4].text
            link_edital = url_pncp_itens
            df_temp.loc[i] = [n_item, objeto, qtd_total, valor_unitario, valor_total,modalidade_itens, link_edital, id_pncp, itens_edital, inicio_rec_proposta, fim_rec_proposta]
        df_itens_pncp = pd.concat([df_itens_pncp, df_temp], ignore_index=True)
        time.sleep(0)
        break
    print(f'Edital {b} de: {dados_limpos.numeroControlePNCP.count()} Finalizado')

df = pd.concat([df, df_itens_pncp], ignore_index=True)

df.to_csv(f'itens_{sigla_uf}_{data_inicial[6:8]}_{data_inicial[4:6]}_{data_inicial[0:4]}.csv', index=False)
df.to_excel(f'itens_{sigla_uf}_{data_inicial[6:8]}_{data_inicial[4:6]}_{data_inicial[0:4]}.xlsx', index=False, engine='openpyxl')
print(f'*** Dataframe Finzalizado, quantidade de itens buscados: {df.shape[0]} ***')
print(f'Editais com erro: {editais_erro}')



# ENVIO DO EMAIL

dia_inicial_relatorio = (f'{str(data_inicial)[6:8]}/{str(data_inicial)[4:6]}/{str(data_inicial)[0:4]}')
dia_final_relatorio = (f'{str(data_final)[6:8]}/{str(data_final)[4:6]}/{str(data_final)[0:4]}')

sender_email = 'seu-email@email.com'
sender_password = 'senha-do-email'
recipients = 'email-remetente@email.com'
subject = 'titulo do email'
body = 'corpo do email'

part = MIMEBase('application', "octet-stream")
part.set_payload(open(f'C:/Users/itens_{sigla_uf}_{data_inicial[6:8]}_{data_inicial[4:6]}_{data_inicial[0:4]}.xlsx', "rb").read())

#### É importante que coloque o local correto do arquivo a ser enviado ####


encoders.encode_base64(part)
part.add_header('Content-Disposition', f'attachment; filename="itens_{sigla_uf}_{data_inicial[6:8]}_{data_inicial[4:6]}_{data_inicial[0:4]}.xlsx"')

message = MIMEMultipart()
message['Subject'] = subject
message['From'] = sender_email
message['To'] = recipients
html_part = MIMEText(body)
message.attach(html_part)
message.attach(part)

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
   server.login(sender_email, sender_password)
   server.sendmail(sender_email, recipients, message.as_string())
   print('Email sent successfully!')
driver.quit()