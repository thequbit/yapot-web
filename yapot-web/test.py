import requests
import json

text = requests.post('http://127.0.0.1:6543/doc', files={'file': open('con-board.pdf','rb')}).text

doc = json.loads(text)

text = requests.get('http://127.0.0.1:6543/doc/{0}'.format(doc['doc_uid'])).text

print text
