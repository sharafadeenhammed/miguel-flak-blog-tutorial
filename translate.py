from app import app
from flask_babel import _
import requests



def translate(language:str, target:str, text:str):
  print(app.config['X_RAPIDAPI_HOST'], app.config['X_RAPIDAPI_KEY'])
  if app.config['X_RAPIDAPI_HOST'] == None or app.config['X_RAPIDAPI_KEY'] == None:
    print('application not configured !!!')
    return _('application not configured for tranlation')
  res = requests.get(
    url = f'https://translated-mymemory---translation-memory.p.rapidapi.com/get?langpair={language}|{target}&q={text}',
    headers={
      'X-RapidAPI-Key':'724473cc58msh81922241d20cda4p1cae60jsna375dfe90556',
      'X-RapidAPI-Host':'translated-mymemory---translation-memory.p.rapidapi.com'
    }
  )
  if res.status_code == 200 and res.json()['responseStatus'] == 200:
    text = res.json()['responseData']['translatedText']
    print('response: ',text)
    return text
  else:
    print('error tranlating !!!')
    return _('Error tranlating post !')
  