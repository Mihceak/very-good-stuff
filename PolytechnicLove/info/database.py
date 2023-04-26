import os
from dotenv import load_dotenv
from pyairtable import Table

from pyairtable.formulas import match

# os.environ['AIRTABLE_TOKEN'] = 'pat2mSXvZ4UytfPj1.feed29df53b575c97ad84ad886ce0d7ed7f03879fbc14eb041f378d65df6ae92'
# os.environ['AIRTABLE_BASE_ID'] = 'appR1M4w95wE99rHp'
load_dotenv()

api_token = os.getenv('AIRTABLE_TOKEN')
base_id = os.getenv('POLYTECHNICLOVE_ID')
player_table = Table(api_key=api_token, base_id=base_id, table_name='Player')
