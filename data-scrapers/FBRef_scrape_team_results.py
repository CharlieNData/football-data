# Scrapes data for individual team pages on FBRef

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

    def get_table_body(div):
        table = div.find('table')
        table_body = table.find('tbody')
        return table_body

    # Get table for goals and assists
    team_schedule_div = soup.find(id="div_kitchen_sink_sched")
    team_schedule_table_body = get_table_body(team_schedule_div)
    team_schedule_features = {'round','goals_for', 'goals_against', 'xg_for', 'xg_against'}

    def parse_table(table, features):
        pre_df = dict()
        rows = table.find_all('tr')
        for row in rows:
            if(row.find('th',{"scope":"row"}) != None):
                for f in features:                    
                    if f == "player":
                        cell = row.find("a")
                    else:
                        cell = row.find("td",{"data-stat": f})
                    a = cell.text.strip().encode()
                    text=a.decode("utf-8")
                    if f in pre_df:
                        pre_df[f].append(text)
                    else:
                        pre_df[f] = [text]
        df = pd.DataFrame.from_dict(pre_df)
        return df

    # general player data
    df_team_schedule = parse_table(team_schedule_table_body, team_schedule_features)

    return df_team_schedule
    
    
def main(argv):
    urls = pd.DataFrame()
    
    try:
        opts, args = getopt.getopt(argv,"hf:",["file="])
    except getopt.GetoptError:
        print('FBref_scrape_team.py -f <url_csv_file>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('FBref_scrape_team.py -f <url_csv_file>')
            sys.exit()
        elif opt in ("-f", "--file"):
            urls = pd.read_csv(arg,delimiter=',')
    
    path = "../data/"
    if not os.path.isdir(path):
        os.mkdir(path)

    for url in urls:
        print(url)
        df_team_schedule = scrapeURL(url)
        
        k = url.rfind("/")
        output_name = url[k+1:]
        df_team_schedule.to_csv(os.path.join(path, output_name+".csv"))
    
if __name__ == "__main__":
   main(sys.argv[1:])