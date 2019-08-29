from bs4 import BeautifulSoup
import pandas as pd
import urllib.request


url = "http://image-net.org/api/text/imagenet.bbox.obtain_synset_wordlist"
ncodes = pd.DataFrame([])


with urllib.request.urlopen(url) as response:
   html = response.read()
   soup = BeautifulSoup(html)
   for code_num,link in enumerate(soup.findAll('a')):
       code = (link.get('href').split("wnid=")[-1])
       values =  link.contents[0]
       ncodes.loc[code_num,"code"] = code
       ncodes.loc[code_num,"name"] = values

ncodes.to_csv("ncodes.csv",index=False)
print (ncodes.shape)