import urllib.request as urllib2
from bs4 import BeautifulSoup
import operator
import psycopg2
from psycopg2.extras import execute_values
import argparse

import json

config={"host":"localhost",
"user":"postgres",
"dbname":"football_data",
"password":"abcd@1234"}



conn=psycopg2.connect(host=config['host'],dbname=config['dbname'],user=config['user'],password=config['password'])
cur=conn.cursor()


def check_tables(country):
	season='season_'+country
	standings='finalstandings_'+country
	cur.execute("""create table if not exists """+season+"""(
		season integer,date character varying ,home_team varchar ,away_team varchar
		,home_goals integer ,away_goals integer ,result varchar)
		"""
		)
	
	cur.execute("""create table if not exists """+ standings+"""(
		season integer ,team varchar,
		points integer ,position integer
		)
		""")
	conn.commit()





def points_total(team,points):
	if team_points.get(team)==None:
		team_points[team]=0
	team_points[team]+=points



def get_page_details(page_url):
	page=urllib2.urlopen(page_url)
	return BeautifulSoup(page, 'html.parser')

def season_table(tup,country):
	query="insert into season_{0} values".format(country)
	query+="%s"
	execute_values(cur,query,tup)
	conn.commit()

def championship_summary(tup,country):
	query="insert into finalstandings_{0} values".format(country)
	query+="%s"
	
	execute_values(cur,query,tup)
	conn.commit()

print("""Select Country: 
		1.England
		2.Spain
		3.Italy
		4.France
		5.Portugal
		6.Netherlands""")

choice=int(input())
if choice==1:
	country='england'
elif choice==2:
	country='spain'
elif choice==3:
	country='italy'
elif choice==4:
	country='france'
elif choice==5:
	country='portugal'
elif choice==6:
	country='netherlands'


check_tables(country)

web_url='http://www.football-data.co.uk/{0}m.php'.format(country)
root_path='http://www.football-data.co.uk/'
team_points={}



links=[]
year=''
soup=get_page_details(web_url)
for link in soup.find_all('a',href=True):
	if link['href'].split('.')[1]=='csv':
		links.append(link['href'])




for link in links:

	if link.split('/')[1]!=year :
		print(link)
		year=link.split('/')[1]
		if year[0]=='0' or year[0]=='1' :
			
			csv_page=get_page_details(root_path+link)
			all_lines=str(csv_page).split('\n')
			all_lines=all_lines[1:]
			season_results=[]

			for line in all_lines:
				i=line.split(',')


				if len(i)>8  and i[1] != '' :
					
					info=(year,i[1],i[2],i[3],i[5],i[8],i[6])
					
					if i[6]=='H':
						points_total(i[2],3)
					elif i[6]=='A':
						points_total(i[3],3)
					else:
						points_total(i[2],1)
						points_total(i[3],1)
				

				season_results.append(info)
				
			a1_sorted_keys = sorted(team_points.items(), key=operator.itemgetter(1),reverse=True)
			pos=1
			position_details=[]
			for i in a1_sorted_keys:
				temp=list(i)
				temp.append(pos)
				temp.insert(0,year)
				position_details.append(tuple(temp))
				pos+=1
			
			team_points={}
			season_table(season_results,country)
			championship_summary(position_details,country)
