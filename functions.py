from selenium.webdriver.common.by import By
import pandas as pd
import smtplib
import os
import mimetypes
from email.message import EmailMessage

def get_item_info(item):
    try:
        name = item.find_element(By.TAG_NAME, "h2").text
        try:
            reviews =  item.find_element(By.XPATH, ".//span[contains(text(), '(') and contains(text(), ')')]")
            reviews = reviews.text
            # 4.5 (120)
            reviews = reviews.split('(')[1].split(')')[0]
        except:
            reviews = 0

        url = item.find_element(By.TAG_NAME, "a").get_attribute("href")

        if int(reviews) > 0:
            df_item = pd.DataFrame({'PRODUTO':[name],"QTD_AVAL":[reviews],"URL":[url]})

            print(f"\nItem encontrado: {name} - {str(reviews)}  - {url}")

            return df_item

    except Exception as e:
        print(f"Erro ao buscar as informações do item {item}. Detalhes: {e}.")
        return False
    
def send_mail_message(sender, password, receiver, subject, text, attachment):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver
    msg.set_content(text)

    try:
        mime_type, _ = mimetypes.guess_type(attachment)

        if mime_type is None:
            mime_type = 'application/octet-stream'  
            mime_type, subtype = mime_type.split('/')

        with open(attachment, 'rb') as arquivo:
            msg.add_attachment(
                arquivo.read(),
                maintype=mime_type,
                subtype=subtype,
                filename=os.path.basename(attachment)
            )

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender, password)
            smtp.send_message(msg)

        print("E-mail enviado com sucesso!")

        return True
    
    except Exception as e:
        print(f"Ocorreu um erro ao enviar o email: {str(e)}")
        return False

        