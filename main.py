from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from time import sleep
import pandas as pd
import openpyxl
import shutil
import os

import constants as c
import functions as f

def main():
    print(f"Conectando com {c.url}...")
    i = 0
    driver = webdriver.Chrome()

    max_retries = int(c.max_retries)

    while i < max_retries:
        i += 1
        driver = webdriver.Chrome()

        try:
            driver.get(c.url)

            # Aguarda até que o input com nome 'Procura no Magalu' esteja visível
            search_bar = WebDriverWait(driver, 1).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[data-testid="input-search"]'))
            )

            search_bar.send_keys(c.search_text)
            print(f"Pesquisando por {c.search_text}...")
            sleep(2)
            search_bar.send_keys(Keys.ENTER)

            print("Página carregada com sucesso!")
            break

        except Exception as e:
            print(f"Tentativa {i}: erro ao localizar a barra de pesquisa. Detalhes: {e}")
            driver.quit()
            if i < 3:
                print("Tentando novamente...")
                sleep(2)

    if i == max_retries:
        raise Exception("Site fora do ar - Não foi possível encontrar a barra de pesquisa do site informado.")

    print("Carregando resultados da pesquisa...")

    sleep(5)
    page = 1

    df_notebooks = pd.DataFrame()
    
    while True:
        print(f"Buscando todos os itens da página {page}...")
        
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "sc-CCtys")))

        page += 1

        notebooks = driver.find_elements(By.CLASS_NAME, "sc-CCtys")


        for item in notebooks:
            df_item = f.get_item_info(item)
            if df_item is not False:
                df_notebooks = pd.concat([df_notebooks,df_item])
            else:
                continue
        
        try:
            next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Go to next page"]')))
            next_button.click()
            sleep(5)
        except:
            print("Última página alcançada ou botão de próxima página não encontrado.")
            break
    
    print(f"Última página alcançada: {page}.")
    df_notebooks = df_notebooks.reset_index(drop=True)

    df_max_reviews = pd.DataFrame() # > 100
    df_min_reviews = pd.DataFrame() # < 100

    for index, row in df_notebooks.iterrows():
        if int(row['QTD_AVAL']) < 100:
            df_min_reviews = pd.concat([df_min_reviews, pd.DataFrame([row])], ignore_index=True)
        else:
            df_max_reviews = pd.concat([df_max_reviews, pd.DataFrame([row])], ignore_index=True)

    output_folder = c.output_folder
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)

    os.makedirs(output_folder)

    file_name = f".{output_folder}{c.output_file}.xlsx"
    print(f"Criando arquivo {file_name}...")

    try:
        with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
            df_min_reviews.to_excel(writer, sheet_name='Piores', index=False)
            df_max_reviews.to_excel(writer, sheet_name='Melhores', index=False)

        print("Arquivo criado com sucesso!")

    except Exception as e:
        msg = (f"Não foi possível criar o arquivo Excel. Motivo: {str(e)}")
        raise Exception(msg)
    
    # Envio de email:
    email_text = """
        Olá, aqui está o seu relatório dos notebooks extraídos da Magazine Luiza.

        Atenciosamente,
        Robô
    """

    email_subject = "Relatório Notebooks"

    send_email = f.send_mail_message(c.email_sender, c.email_password, c.email_receiver, email_subject, email_text, file_name)
    
    if send_email is False:
        raise Exception("Falha ao enviar o email.")
    
    print(f"Email para {c.email_receiver} enviado com sucesso!")
if __name__=="__main__":
    main()