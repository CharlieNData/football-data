# Original code from https://github.com/chmartin/FBref_EPL/blob/master/FBref_scrape.py 

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os, re
import sys, getopt
import csv

def scrapeURL(url, table_type):
    res = requests.get(url)
    
    # The type of table we are looking to parse
    squad_div_id = "div_stats_"+table_type+"_squads"
    player_div_id = "div_stats_"+table_type

    ## The next two lines get around the issue with comments breaking the parsing.
    comm = re.compile("<!--|-->")
    soup = BeautifulSoup(comm.sub("",res.text),'lxml')
    squad_div = soup.find(id=squad_div_id)
    players_div = soup.find(id=player_div_id)

    def get_table_body(div):
        table = div.find('table')
        table_body = table.find('tbody')
        return table_body

    squad_table_body = get_table_body(squad_div)
    players_table_body = get_table_body(players_div)

    #Parse team_table
    #Note: features does not contain squad name, it requires special treatment
    features_wanted_squad = {"squad","passes_pressure","passes_completed","passes"}
    features_wanted_player = {"player","squad","position","minutes_90s","passes_pressure","passes_completed","passes","through_balls"}
    def parse_table(table, features):
        pre_df = dict()
        rows = table.find_all('tr')
        for row in rows:
            if(row.find('th',{"scope":"row"}) != None):
                for f in features:
                    if f == "player":
                        cell = row.find("a")
                    elif f == "squad":
                        cell = row.select("a[href*=squads]")[0]
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
    
    df_squad = parse_table(squad_table_body, features_wanted_squad)
    df_players = parse_table(players_table_body, features_wanted_player)

    return (df_squad, df_players)
    
    
def main(argv):
    urls = pd.DataFrame()
    table_type = "passing_types"

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
        (df_squad, df_players) = scrapeURL(url, table_type)
        
        k = url.rfind("/")
        output_name = url[k+1:]
        df_squad.to_csv(os.path.join(path, output_name+"_squad_"+table_type+".csv"))
        df_players.to_csv(os.path.join(path, output_name+"_players_"+table_type+".csv"))
    

if __name__ == "__main__":
   main(sys.argv[1:])