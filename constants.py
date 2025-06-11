import os 
from dotenv import load_dotenv

load_dotenv()

# CRAWLER ENV
url = os.getenv('url')
max_retries = os.getenv('max_retries')
search_text = os.getenv('search_text')

# EXCEL ENV
output_folder = os.getenv('output_folder')
output_file = os.getenv('output_file')

# EMAIL ENV
email_sender = os.getenv('email_sender')
email_password = os.getenv('email_password')
email_receiver = os.getenv('email_receiver')