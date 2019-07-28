import os
import json
import requests

with open('crawledData/pubUrls.json','r') as urlListFile:
    urlList = json.load(urlListFile)

headers = {'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15'}

for record in urlList:
    url = record['url']
    header = record['header']
    title = record['title']

    response = requests.get(url,headers=headers)

    directory = 'papers/'+header+'/';
    if not os.path.exists(directory):
        os.makedirs(directory)
    try:
        file = open(directory+title+'.pdf','wb')
    except Exception as e:
        file = open(directory+'paper-'+str(hash(title))+'.pdf','wb')
    finally:
        for content in response.iter_content():
            file.write(content)
        print(file.name)
        file.close()