# Original code from https://github.com/chmartin/FBref_EPL/blob/master/FBref_scrape.py 

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os, re
import sys, getopt
import csv

def scrapeURL(url):
    res = requests.get(url)
    ## The next two lines get around the issue with comments breaking the parsing.
    comm = re.compile("<!--|-->")
    soup = BeautifulSoup(comm.sub("",res.text),'lxml')
    squad_passing_table = soup.find(id="stats_passing_squads")
    squad_passing_table_body = squad_passing_table.find('tbody')

    #Parse team_table
    pre_df_squad = dict()
    #Note: features does not contain squad name, it requires special treatment
    features_wanted_squad = {"passes_completed","passes","passes_pct","passes_total_distance","passes_progressive_distance"}
    rows_squad = squad_passing_table_body.find_all('tr')
    for row in rows_squad:
        if(row.find('th',{"scope":"row"}) != None):
            name = row.find('th',{"data-stat":"squad"}).text.strip().encode().decode("utf-8")
            if 'squad' in pre_df_squad:
                pre_df_squad['squad'].append(name)
            else:
                pre_df_squad['squad'] = [name]
            for f in features_wanted_squad:
                cell = row.find("td",{"data-stat": f})
                a = cell.text.strip().encode()
                text=a.decode("utf-8")
                if f in pre_df_squad:
                    pre_df_squad[f].append(text)
                else:
                    pre_df_squad[f] = [text]
    df_squad = pd.DataFrame.from_dict(pre_df_squad)
    
    return df_squad
    
    
def main(argv):
    urls = pd.DataFrame()
    
    try:
        opts, args = getopt.getopt(argv,"hf:",["file="])
    except getopt.GetoptError:
        print('FBref_scrape.py -f <url_csv_file>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('FBref_scrape.py -f <url_csv_file>')
            sys.exit()
        elif opt in ("-f", "--file"):
            urls = pd.read_csv(arg,delimiter=',')
    
    path = "../data/"
    if not os.path.isdir(path):
        os.mkdir(path)

    for url in urls:
        print(url)
        df_squad = scrapeURL(url)
        
        k = url.rfind("/")
        output_name = url[k+1:]
        df_squad.to_csv(os.path.join(path, output_name+"_squad_passing.csv"))
    


if __name__ == "__main__":
   main(sys.argv[1:])