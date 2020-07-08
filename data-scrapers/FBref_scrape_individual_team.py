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
    player_general_div = soup.find(id="div_kitchen_sink_standard")
    player_general_table_body = get_table_body(player_general_div)
    features_wanted_player_general = {"player", "nationality","position","age", "minutes", "goals", "goals_per90", "assists", "assists_per90", "xg_per90", "xa_per90", "npxg_per90"}

    # Get table for defensive actions
    player_defence_div = soup.find(id="div_kitchen_sink_defense")
    player_defence_table_body = get_table_body(player_defence_div)
    features_wanted_player_defence = {"player","nationality","position","age","minutes_90s","dribble_tackles","dribbles_vs","dribble_tackles_pct","pressures","pressure_regains","pressure_regain_pct"}

    # Get table for team passing stats
    player_passing_div = soup.find(id="div_kitchen_sink_passing")
    player_passing_table_body = get_table_body(player_passing_div)
    features_wanted_player_passing = {"player", "nationality","position","age", "minutes_90s", "passes_completed", "passes", "passes_pct", "passes_progressive_distance"}

    # Get table for team possession stats
    player_possession_div = soup.find(id="div_kitchen_sink_possession")
    player_possession_table_body = get_table_body(player_possession_div)
    features_wanted_player_possession = {"player", "nationality","position","age", "minutes_90s", "carry_progressive_distance"}

    # Get table for goal and shot creation
    gca_div = soup.find(id="div_kitchen_sink_gca")
    gca_table_body = get_table_body(gca_div)
    features_wanted_gca = {"player", "nationality", "position", "age", "minutes_90s", "sca", "sca_per90", "gca", "gca_per90"}

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
    df_player_general = parse_table(player_general_table_body, features_wanted_player_general)

    # defensive player data
    df_player_defensive = parse_table(player_defence_table_body, features_wanted_player_defence)

    # passing player data
    df_player_passing = parse_table(player_passing_table_body, features_wanted_player_passing)

    # possession player data
    df_player_possession = parse_table(player_possession_table_body, features_wanted_player_possession)

    # gca data
    df_player_gca = parse_table(gca_table_body, features_wanted_gca)

    return df_player_general, df_player_defensive, df_player_passing, df_player_possession, df_player_gca
    
    
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
        df_player_general, df_player_defence, df_player_passing, df_player_possession, df_gca = scrapeURL(url)
        
        k = url.rfind("/")
        output_name = url[k+1:]
        df_player_general.to_csv(os.path.join(path, output_name+"_players_general.csv"))
        df_player_defence.to_csv(os.path.join(path, output_name+"_players_defensive.csv"))
        df_player_passing.to_csv(os.path.join(path, output_name+"_players_passing.csv"))
        df_player_possession.to_csv(os.path.join(path, output_name+"_players_possession.csv"))
        df_gca.to_csv(os.path.join(path, output_name+"_players_gca.csv"))
    
if __name__ == "__main__":
   main(sys.argv[1:])