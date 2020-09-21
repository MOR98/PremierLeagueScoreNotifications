##Note this is untested on this seasons teams, it works on last seasons teams until
##it reaches the relegated teams
##If you run it on future games it will give the fixtures and game times

import time
import datetime
from win10toast import ToastNotifier
from bs4 import BeautifulSoup
from bs4.element import Comment
import requests

#Toast to show online
toaster = ToastNotifier()
toaster.show_toast("Score Alerts Online", "Premier League Live Score Alerts", threaded=True,
                   icon_path='pl_icon.ico' , duration=None)  

#get games from the bbc site and return the games as a list
def getGames():
	#request and parse text from the html
	url ='https://www.bbc.com/sport/football/premier-league/scores-fixtures/2020-09'
	res = requests.get(url)	
	html_page = res.content
	soup = BeautifulSoup(html_page, 'html.parser')
	text = soup.find_all(text=True)

	output = ''

	#we need to first remove unwanted words, some are html based others are extra team names
	blacklist = [
		'[document]',
		'noscript',
		'header',
		'html',
		'meta',
		'head', 
		'input',
		'script',
		'Manchester',
		'United',
		'Palace',
		'Villa',
		'West',
		'Albion',
		'Hotspur',
		'Hove',
		'&',
		'Wolverhampton',
		'Wanderers',
		'Man',
		'Sheffield'
	]
	#these are unique team names to look for
	teams = [
		'City',
		'Utd',
		'Liverpool',
		'Fulham',
		'Arsenal',
		'Leeds',
		'Everton',
		'Southampton',
		'Tottenham',
		'Brighton',
		'Aston',
		'Wolves',
		'Sheff',
		'Ham',
		'Bromwich',
		'Crystal',
		'Leicester',
		'Newcastle',
		'Chelsea',
		'Burnley'
	]

	#Remove blacklisted words from the text some of these are sudonames
	#for team's links so we dont want that
	for t in text:
		if (t.parent.name not in blacklist):
			output += '{} '.format(t)
	words = output.split()
	
	#Using two keywords to flag the start and end of the score info.
	gamesA = []
	flag = 0
	for i in words:
		if( flag == 1 and i not in blacklist):
			gamesA.append(i)

		if(i == 'Content'):flag = 1
		if(i == 'All'):flag =0
	
	#Team names are duplicated by links, some teams also have similar names 
	#So we remove to use single unique words for teams
	i = 0
	while(i<len(gamesA)):
		if(gamesA[i]==gamesA[i-1]):
			gamesA[i-1]=" "
		if(gamesA[i-1]=="Sheff" and gamesA[i]=="Utd"):
			del gamesA[i]
		if(gamesA[i-1]=="Leicester" and gamesA[i]=="City"):
			del gamesA[i]
		i +=1

	#G will store the score information, scores are of the format Team score Team score
	#So we fill accordingly
	G = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
	elem = 0
	count = 0
	#loop through the text, pull out the team names and scores
	for i in gamesA:

		#First piece of each game element is the first team
		if(i in teams and elem == 0):
			G[count][elem] = i
			elem = 1
		#Followed by the non team info (score or time)
		elif(elem ==1 and i not in teams):
			G[count][elem] = i
			elem = 2
		#Then if the next piece is another team, add that and go to piece 4
		elif(elem == 2 and i  in teams):
			G[count][elem] = i
			elem = 3
		#Or of not, just add the extra  information
		elif(elem == 2 and i not in teams):
			G[count][elem] = i
		#Then add the second team info
		elif(elem == 3 and i not in teams):
			G[count][elem] = i
			elem = 0
			count +=1
		#At this point if we find another team we start a new game element
		elif(elem == 3 and i in teams):
			count +=1
			G[count][0] = i
			elem = 1
	#return list of game strings
	return G

def teamGoalinfo(team):
		#this function is used to match unique keywords to full team name text and icon path.
		case = str(team)

		if  case == "City":
			text = "Man City Score!"
			ico  = "mci.ico"
		elif case == "Utd":
			text = "Man Utd Score!"
			ico  = "utd.ico"
		elif case == "Liverpool":
			text = "Liverpool Score!"
			ico  = "liv.ico"
		elif case == "Chelsea":
			text = "Chelsea Score!"
			ico  = "chl.ico"
		elif case == "Fulham":
			text = "Fulham Score!"
			ico  = "fha.ico"
		elif case == "Leicester":
			text = "Leicester Score!"
			ico  = "lei.ico"
		elif case == "Newcastle":
			text = "Newcastle Score!"
			ico  = "ncs.ico"
		elif case == "Ham":
			text = "West Ham Score!"
			ico  = "ham.ico"
		elif case == "Aston":
			text = "Aston Villa Score!"
			ico  = "vil.ico"
		elif case == "Everton":
			text = "Everton Score!"
			ico  = "evt.ico"
		elif case == "Bromwich":
			text = "West Brom Score!"
			ico  = "wba.ico"
		elif case == "Crystal":
			text = "Crystal Palace Score!"
			ico  = "pal.ico"
		elif case == "Tottenham":
			text = "Tottenham Score!"
			ico  = "ths.ico"
		elif case == "Southampton":
			text = "Southampton Score!"
			ico  = "sfc.ico"
		elif case == "Burnley":
			text = "Burnley Score!"
			ico  = "bfc.ico"
		elif case == "Wolves":
			text = "Wolves Score!"
			ico  = "wfc.ico"
		elif case == "Sheff":
			text = "Sheffield Utd Score!"
			ico  = "sut.ico"
		elif case == "Leeds":
			text = "Leeds Score!"
			ico  = "lds.ico"
		elif case == "Brighton":
			text = "Brighton & Hove Albion Score!"
			ico  = "brf.ico"
		elif case == "Arsenal":
			text = "Arsenal Score!"
			ico  = "ars.ico"
		
		#return path and text
		return text,ico


#Get initial scores
games = getGames()

while (True):
	#grab the latest scores
	currentGames = getGames()
	k=0
	i=0

	#check each game 
	for k in range (len(currentGames)):
		#for debug
		print(currentGames[k])
		print('------------------------')

		#if the score of team 1 is different they scored toast accordingly
		if((currentGames[k][1] != games[k][1]) and currentGames[k][3] == games[k][3]):
			#first team scored
			text,ico = teamGoalinfo( currentGames[k][0] )
			gameinfo=  str(currentGames[k][0])+" "+ str(currentGames[k][1])+"-"+str(currentGames[k][3])+" "+str(currentGames[k][2])

			toaster.show_toast(text, gameinfo, threaded=True,
                   icon_path=ico, duration=None)
			time.sleep(1)

		#if the score of team 2 is different they scored toast accordingly
		if((currentGames[k][1] == games[k][1]) and currentGames[k][3] != games[k][3]):
			#Second team scored
			text,ico = teamGoalinfo( currentGames[k][2] )
			gameinfo=  str(currentGames[k][0])+" " + str(currentGames[k][1])+"-"+str(currentGames[k][3])+" "+str(currentGames[k][2])

			toaster.show_toast( text,gameinfo ,threaded=True,
                   icon_path=ico, duration=None)
			time.sleep(1)

		#If the "score var goes from text (game time or something) to an int the game started it is 0-0, kick off"
		if((type(currentGames[k][1])==int) and (type(games[k][1])==str)):
			#this means kick off
			text = str(currentGames[k][0]) + " vs " + str(currentGames[k][2]) + ": kick off"
			dummy,ico = teamGoalinfo(currentGames[k][0])
			toaster.show_toast(text, text, threaded=True,
                   icon_path=ico, duration=None)
			time.sleep(1)

	print('========================')
	#reset the previous games holder
	games = currentGames
	time.sleep(30)

