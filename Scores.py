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
	G =[]
	elem = 0
	count = 0
	#loop through the text, pull out the team names and scores
	for i in gamesA:
		#First piece of each game element is the first team
		if(i in teams and elem == 0):
			G.append(str(i))
			elem = 1
		#Followed by the non team info (score or time)
		elif(elem ==1 and i not in teams):
			G[count] = G[count]+ " " + str(i)
			elem = 2
		#Then if the next piece is another team, add that and go to piece 4
		elif(elem == 2 and i  in teams):
			G[count] = G[count]+ " " + str(i)
			elem = 3
		#Or of not, just add the extra  information
		elif(elem == 2 and i not in teams):
			G[count] = G[count]+  " " +str(i)
		#Then add the second team info
		elif(elem == 3 and i not in teams):
			G[count] = G[count]+ " " + str(i)
			elem = 0
			count +=1
		#At this point if we find another team we start a new game element
		elif(elem == 3 and i in teams):
			count +=1
			G.append(str(i))
			elem = 1
	#return list of game strings
	return G

#Get initial scores
games = getGames()

while (True):
	#grab the latest scores
	currentGames = getGames()
	k=0
	#check each game for changes 
	for i in currentGames:
		print(currentGames[k])
		print('------------------------')
		if currentGames[k] != games[k]:
			#toast to windows notifications if a change is made
			print("Update in Game: " ,currentGames[k])
			toaster.show_toast("New Score!", str(currentGames[k]), threaded=True,
                   icon_path='pl_icon.ico', duration=None)
			time.sleep(1)
		k +=1
	print('========================')
	#reset the previous games holder
	games = currentGames
	time.sleep(30)
