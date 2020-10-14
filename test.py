from bs4 import BeautifulSoup
import re

with open("C:/Users/bonfardeci-j/source/repos/dl_repos/hello-world-2-spider/html/imdb_profiles/AdamDriver.html", encoding="utf-8") as html:
    soup = BeautifulSoup(html, 'html.parser')
    awards = [span for span in soup.select("span.awards-blurb") if re.search(r'(wins|nominations)', span.text)]
    if len(awards) > 0:
        wins = re.findall(r'\d+(?=\swins)', awards[0].text)
        print(int(wins[0]))


    
    
        

