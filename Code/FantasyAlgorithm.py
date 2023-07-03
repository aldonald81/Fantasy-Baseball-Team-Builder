"""
DRAFTKING.py
Alexander Donald and Gabriel Levy
"""


import pandas as pd
import numpy as np
import glob
import random
import math
import copy
import csv



positions = ['catcher', 'firstbase', 'secondbase', 'thirdbase',
             'shortstop', 'outfield', 'outfield', 'outfield', 'dh',
             'starter', 'starter', 'starter', 'starter', 'starter',
             'reliever', 'reliever', 'reliever', 'reliever', 'reliever']

pricecsvs = ['FantasyPriceCatcher.csv', 'FantasyPriceFirstBase.csv', 'FantasyPriceSecondBase.csv'
,'FantasyPriceThirdBase.csv','FantasyPriceShortstop.csv','FantasyPriceOutfield.csv',
             'FantasyPriceStarter.csv', 'FantasyPriceReliever.csv']

statscsvs = ['FantasyStatsHitters.csv', 'FantasyStatsPitchers.csv']

positioni = ['catcher', 'firstbase', 'secondbase', 'thirdbase',
             'shortstop', 'outfield', 'starter', 'reliever']

genSize = 50
budget = 200
numGens = 1000
numCross = .8
numMut = .15
numRep = .05

        

def createInitialGen(prices, stats):
    teams = []
    i = 0
    while i<genSize:
        team = []
        teamprices = []
        teampoints = []
        
        for pos in positions:
            if pos == 'dh':
                index = random.randint(0,5)
                position = list(prices)[index]
                dict = prices[position]
                dh = random.choice(list(dict))
                price = prices[position][dh]
                points = stats['hitters'][dh]
                team.append(dh)
                teamprices.append(price)
                teampoints.append(points)
            else:
                if pos != 'starter' and pos != 'reliever':
                    dict = prices[pos]
                    hitter = random.choice(list(dict))
                    price = prices[pos][hitter]
                    points = stats['hitters'][hitter]
                    team.append(hitter)
                    teamprices.append(price)
                    teampoints.append(points)
                else:
                    dict = prices[pos]
                    pitcher = random.choice(list(dict))
                    price = prices[pos][pitcher]
                    points = stats['pitchers'][pitcher]
                    team.append(pitcher)
                    teamprices.append(price)
                    teampoints.append(points)
        team1 = [team, teamprices, teampoints]
        if sum(teamprices) <= budget and not duplicate(team1):
            info = [team, teamprices, teampoints]
            teams.append(info)
            i+=1
    
    return teams



def crossover(team1, team2):
    # Pick random crossover position
    # crossover point INCLUDED in right section of crossover
    # Limit crossover points to these indexes so we don't have deal with crossing
    # over in the middle of the pitchers leading to duplicates
    indexes = [0,1,2,3,4,5,8,9,14]
    crossoverIndex = random.choice(indexes)

    #keep the left part of team1 and the right part of team2 with those respective teams
    team1[0] = team1[0][0:crossoverIndex] + team2[0][crossoverIndex:]
    team2[0] = team2[0][0:crossoverIndex] + team1[0][crossoverIndex:]

    #Update the price arrays at the same point
    team1[1] = team1[1][0:crossoverIndex] + team2[1][crossoverIndex:]
    team2[1] = team2[1][0:crossoverIndex] + team1[1][crossoverIndex:]

    #Update the score arrays at the same point
    team1[2] = team1[2][0:crossoverIndex] + team2[2][crossoverIndex:]
    team2[2] = team2[2][0:crossoverIndex] + team1[2][crossoverIndex:]

    return team1, team2


def mutateSelectively(team, prices, stats):
    #SELECTIVE mutation
    mutationIndex, method = selectiveMutation(team)
    #print(mutationIndex)
    playerPosition = positions[mutationIndex]
    newPlayer = ""
    price = 0
    points = 0

    # mutate for player that improves value
    if method == "value":
        #Player to be mutated points to price ratio - want it to be higher
        mutatedPlayerRatio = team[2][mutationIndex]/ team[1][mutationIndex]
        newPlayerRatio = -100000 #arbirary starting value that makes sure while loop is entered
        #loop until you find a player at a BETTER value
        while (newPlayerRatio < mutatedPlayerRatio):
            if playerPosition == 'dh':
                index = random.randint(0,5)
                position = list(prices)[index]
                dict = prices[position]
                newPlayer = random.choice(list(dict))
                points = stats['hitters'][newPlayer]

                #Reset player position to their actual position that's listed in prices
                playerPosition = position
                price = prices[playerPosition][newPlayer]
            else:
                if playerPosition != 'starter' and playerPosition != 'reliever':
                    dict = prices[playerPosition]
                    newPlayer = random.choice(list(dict))
                    points = stats['hitters'][newPlayer]
                    price = prices[playerPosition][newPlayer]
                else:
                    dict = prices[playerPosition]
                    newPlayer = random.choice(list(dict))
                    points = stats['pitchers'][newPlayer]
                    price = prices[playerPosition][newPlayer]
            
            newPlayerRatio = points/price
            newPlayerPoints = points


    #mutate for player that improves points
    else:
        newPlayerPoints = -1000

        #loop until you find a player with better POINTS
        while (newPlayerPoints < team[2][mutationIndex]):
            if playerPosition == 'dh':
                index = random.randint(0,5)
                position = list(prices)[index]
                dict = prices[position]
                newPlayer = random.choice(list(dict))
                points = stats['hitters'][newPlayer]

                #Reset player position to their actual position that's listed in prices
                playerPosition = position
                price = prices[playerPosition][newPlayer]
            else:
                if playerPosition != 'starter' and playerPosition != 'reliever':
                    dict = prices[playerPosition]
                    newPlayer = random.choice(list(dict))
                    points = stats['hitters'][newPlayer]
                    price = prices[playerPosition][newPlayer]
                else:
                    dict = prices[playerPosition]
                    newPlayer = random.choice(list(dict))
                    points = stats['pitchers'][newPlayer]
                    price = prices[playerPosition][newPlayer]
            
            newPlayerPoints = points

    

    # Mutate the player
    team[0][mutationIndex] = newPlayer
    # Change the price accordingly
    team[1][mutationIndex] = price
    # Change the points accordingly
    team[2][mutationIndex] = points

    return team




def mutate(team, prices, stats):
    #RANDOM mutation
    mutationIndex = random.randint(0, len(positions)-1)
    playerPosition = positions[mutationIndex]   


    # Get a new better player based off playerPosition
    if playerPosition == 'dh':
        index = random.randint(0,5)
        position = list(prices)[index]
        dict = prices[position]
        newPlayer = random.choice(list(dict))
        points = stats['hitters'][newPlayer]

        #Reset player position to their actual position that's listed in prices
        playerPosition = position
        price = prices[playerPosition][newPlayer]
    else:
        if playerPosition != 'starter' and playerPosition != 'reliever':
            dict = prices[playerPosition]
            newPlayer = random.choice(list(dict))
            points = stats['hitters'][newPlayer]
            price = prices[playerPosition][newPlayer]
        else:
            dict = prices[playerPosition]
            newPlayer = random.choice(list(dict))
            points = stats['pitchers'][newPlayer] 
            price = prices[playerPosition][newPlayer]
    

    # Mutate the player
    team[0][mutationIndex] = newPlayer
    # Change the price accordingly
    team[1][mutationIndex] = price
    # Change the points accordingly
    team[2][mutationIndex] = points

    return team


def selectiveMutation(team):
    worst = 0
    mutationIndex = 0

    #ONLY IF COST OF TEAM IS WITHIN X OF 200 USE VALUE AS METRIC 
        #ELSE FIND PLAYER WITH LOWEST POINTS
        # should we divide between hitters and pitchers??? Yes i think so since the scales are a bit different
    
    
    #Randomly select whether player will be hitter or pitcher
    hitOrPitch = random.randint(0,1)
    
    #Case when we want to select a hitter index
    if hitOrPitch == 0:
        if(sum(team[1]) >= .9*budget):
            method = "value"
            for i in range(0,9):
                diff = team[2][i]/sum(team[2]) - team[1][i]/sum(team[1])
                if diff<worst:
                    worst = diff
                    mutationIndex = i
        else:
            method = "points"
            worst = team[2][0]
            for i in range(0, 9):
                points = team[2][i]
                if points<worst:
                    worst = points
                    mutationIndex = i
    
    #Case when we want to select a hitter index
    else:
        if(sum(team[1]) >= .9*budget):
            method = "value"
            for i in range(9, len(team[0])):
                diff = team[2][i]/sum(team[2]) - team[1][i]/sum(team[1])
                if diff<worst:
                    worst = diff
                    mutationIndex = i
        else:
            method = "points"
            worst = team[2][0]
            for i in range(9, len(team[0])):
                points = team[2][i]
                if points<worst:
                    worst = points
                    mutationIndex = i
    
    return mutationIndex, method



def duplicate(team):
    dict1hit = {}
    dict1pitch = {}
    for player in range(len(team[0])):
        if player<9:
            if team[0][player] in dict1hit:
                dict1hit[team[0][player]] += 1
            else:
                dict1hit[team[0][player]] = 1
        else:
            if team[0][player] in dict1pitch:
                dict1pitch[team[0][player]] += 1
            else:
                dict1pitch[team[0][player]] = 1
   
    for player in dict1hit:
        if dict1hit[player]>1:
            return True
    for player in dict1pitch:
        if dict1pitch[player]>1:
            return True
    return False




def algorithm():
    prices = {}
    for i in range(len(pricecsvs)):
        data = pd.read_csv(pricecsvs[i])
        prices[positioni[i]] = {}
        for row in range(len(data)):
            name = data.iloc[row, 0].split(' - ')[0]
            price = int(data.iloc[row, 1][1:])
            prices[positioni[i]][name] = price
            
    stats = {}
    stats['hitters'] = {}
    stats['pitchers'] = {}
    for i in range(len(statscsvs)):
        data = pd.read_csv(statscsvs[i])
        for row in range(len(data)):
            name = data.iloc[row,1] + ' ' + data.iloc[row,0]
            name = name[1:]
            if i==0:
                if (name in prices['catcher']) or (name in prices['firstbase']) or (name in prices['secondbase']) or (name in prices['thirdbase']) or (name in prices['shortstop']) or (name in prices['outfield']):
                    stats['hitters'][name] = data.iloc[row,25]
            else:
                if (name in prices['starter']) or (name in prices['reliever']):
                    stats['pitchers'][name] = data.iloc[row,22]
    
    
    for pos in prices:
        to_be_removed = []
        for player in prices[pos]:
            if pos == 'starter' or pos == 'reliever':
                if player not in stats['pitchers']:
                    to_be_removed.append(player)
            else:
                if player not in stats['hitters']:
                    to_be_removed.append(player)
        for player in to_be_removed:
            prices[pos].pop(player)

    
    
    teams = createInitialGen(prices, stats)
    

    for gen in range(numGens):
        #print("GENERATION " + str(gen))
        fitnesses = []
        for team in teams:
            fitnesses.append(sum(team[2]))
        
        
        sumfit = sum(fitnesses)
        fitnesses = fitnesses/sumfit
         
        
        crossovers = []
        for i in range(int(numCross*genSize)):
            r = random.random()
            for fit in range(len(fitnesses)):
                if r<sum(fitnesses[0:fit+1]):
                    crossovers.append(fit)
                    break

        
        mutations = []
        for i in range(int(numMut*genSize)):
            if i == 0:
                mutations.append(np.where(fitnesses==max(fitnesses))[0][0])
            else:
                #Always mutate the top one --- might help one score gets high
                #Also are we accounting for the possibility of multiple instance of the same index????????????????????
                r = random.random()
                for fit in range(len(fitnesses)):
                    if r<sum(fitnesses[0:fit+1]):
                        mutations.append(fit)
                        break


        reproductions = []
        for i in range(int(numRep*genSize)):
            if i==0:
                reproductions.append(np.where(fitnesses==max(fitnesses))[0][0])
            else:
                r = random.random()
                fit = 0
                while fit<len(fitnesses):
                    #print(fit)
                    if fitnesses[fit] != max(fitnesses):
                        if r<sum(fitnesses[0:fit+1]):
                            reproductions.append(fit)
                            break
                    fit += 1
    
        
        newGen = []
        for i in range(len(crossovers)//2):
            team1, team2 = crossover(copy.deepcopy(teams[crossovers[i]]), copy.deepcopy(teams[crossovers[i+1]]))
            k = 0   
            while (sum(team1[1])>budget or sum(team2[1])>budget or duplicate(team1) or duplicate(team2)) and k<5:
                team1, team2 = crossover(copy.deepcopy(teams[crossovers[i]]), copy.deepcopy(teams[crossovers[i+1]]))
                k+=1
            if sum(team1[1])>budget or sum(team2[1])>budget or duplicate(team1) or duplicate(team2):
                newGen.append(copy.deepcopy(teams[crossovers[i]]))
                newGen.append(copy.deepcopy(teams[crossovers[i+1]]))
            else:
                newGen.append(team1)
                newGen.append(team2)
        
        
        for i in range(len(mutations)):
            #createCopy(...)
            #team = mutate(copy.deepcopy(teams[mutations[i]]), prices, stats)
            team = mutateSelectively(copy.deepcopy(teams[mutations[i]]), prices, stats)
            j=0
            while (sum(team[1])>budget or duplicate(team)) and j<10:
                #team = mutate(copy.deepcopy(teams[mutations[i]]), prices, stats)
                team = mutateSelectively(copy.deepcopy(teams[mutations[i]]), prices, stats)
                j+=1
            if (sum(team[1])>budget or duplicate(team)):
                newGen.append(copy.deepcopy(teams[mutations[i]]))
                #print("****************************************8")
            else:
                newGen.append(team)
        
        for i in range(len(reproductions)):
            newGen.append(copy.deepcopy(teams[reproductions[i]]))



        teams = copy.deepcopy(newGen)


        # Find top team after each generation
        fitnesses = []
        for team in teams:
            fitnesses.append(sum(team[2]))
            #print(sum(team[2]))
        
        max_index = np.where(fitnesses==max(fitnesses))[0][0]
        
    print("---------------------------------------------------")
    print("TEAM")
    print(teams[max_index])
    print("TOTAL COST")
    print(sum(teams[max_index][1]))
    print("TOTAL POINTS")
    print(sum(teams[max_index][2]))
    print("---------------------------------------------------")

    # with open('Experiments.csv', 'w') as file:
    #     mywriter = csv.writer(file)
    #     mywriter.writerows([teams[max_index][0]]) 
    #     mywriter.writerows([teams[max_index][1]]) 
    #     mywriter.writerows([teams[max_index][2]]) 
    
    #pointTotal = sum(teams[max_index][2])

    #costTotal = sum(teams[max_index][1])

    return teams[max_index]
    

algorithm()


"""

playerOccurances = {}

bestScore = 0
bestTeam = []

for i in range(20):
    team  = algorithm() 

    if sum(team[2]) > bestScore:
        bestScore = sum(team[2])
        bestTeam = team

    for j in range(len(team[0])):
        name = team[0][j]
        if(name == "Will Smith" and j<9):
            name = "Will Smith (hitter)"
        
        elif name == "Will Smith" and j>=9:
            name = "Will Smith (pitcher)"

        elif(name == "Shohei Ohtani" and j<9):
            name = "Shohei Ohtani (hitter)"
        
        elif name == "Shohei Ohtani" and j>=9:
            name = "Shohei Ohtani (pitcher)"


        if name in playerOccurances:
            playerOccurances[name] += 1
        else:
            playerOccurances[name] = 1

#print(playerOccurances)

print("BEST TEAM")
print(bestTeam)
print(bestScore)


with open('playerOccurances.csv', 'w') as file:
    mywriter = csv.writer(file, delimiter=',')

    for key in playerOccurances:
        #print(key)
        mywriter.writerow([key, str(playerOccurances[key])]) 

"""