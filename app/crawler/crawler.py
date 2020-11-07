import json
import requests
from bs4 import BeautifulSoup
import pymongo

# start_url = 'https://stackoverflow.com'

class Crawler():
    #connect to cloud mongo
    client = pymongo.MongoClient('mongodb+srv://bipul:9818959573@searchengine-ybruq.mongodb.net/khoj?retryWrites=true&w=majority')

    #create db client
    db = client.khoj
    #response result storage
    search_results = []

    #crawl domain
    def crawl(self, url, depth):
        #perform HTTP GET request
        try:
            print('Crawling url: "%s" at depth: %d' % (url, depth))
            response = requests.get(url, headers={'user-agent': 'Khoj.com'})
        except:
            print('failed to perform HTTP GET request on "%s"\n' % url)
            return
        #parse page content
        content = BeautifulSoup(response.text, 'lxml')

        #try to extract page title and description
        try:
            title = content.find('title').text
            description = ''
            
            for tag in content.find_all():
                if tag.name == 'p':
                    description += tag.text.strip().replace('\n', '')
        except:
            return

        #store the result structure
        result ={
            'url': url,
            'title': title,
            'description': description
        }
        #print('\n\nReturn:\n\n',json.dumps(result, indent=2))

        search_results = self.db.search_results
        search_results.insert_one(result)
        search_results.create_index([
            ('url', pymongo.TEXT),
            ('title', pymongo.TEXT),
            ('description', pymongo.TEXT)
        ], name='search_results', default_language='english')
        
        
        #store the result to the data list
        #self.search_results.append(result)

        #return when the depth is exhausted
        if depth == 0:
            return

        #extract all the available links on the page
        links = content.find_all('a')

        #loop over links
        for link in links:
            #try to crawl links recursively
            try:
                #links with 'http' gets crawled 
                if 'http' in link['href']:
                    self.crawl(link['href'], depth - 1)
            #ignore if any errors
            except KeyError:
                pass
    
        #close connection
        client.close()
      

crawler = Crawler()

crawler.crawl('https://onlinekhabar.com', 1)

'''with open('data.json', 'w') as json_file:
    file_content = ''
    for entry in data:
        file_content += (json.dumps(entry, indent=2))

    json_file.write(file_content)

'''
#print(json.dumps(result, indent=2))