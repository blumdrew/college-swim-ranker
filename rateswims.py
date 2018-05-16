import numpy as np
import os

#function to get team from team ID
def get_team_from_id(team_id):
    dir_name = os.path.dirname(__file__)
    team_id_path = os.path.join(dir_name, '/team and meet ids')
    os.chdir('team_id_path')
    with open('team ids.txt') as file:
        #iterate through all lines in team ID file and find correct team name
        for line in file:
            current_id = line.split('=')[1][:-1]
            current_team = line.split('=')[0][:-3]
            if current_id==str(team_id):
                #if id in line matches input ID, return team name and change back to dir
                os.chdir(dir_name)
                return current_team
    #if function reaches this, change dir and return unknown team
    os.chdir(dir_name)
    return 'Unknown Team'

#test if a string is an int or not
def is_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

#score all swims from a meet, rank them
def score_swims(file_in='2018 NCAA Division I Mens Championships.txt'):
    #need to make sure in the right dir
    dir_name = os.path.dirname(__file__)
    meet_data_path = os.path.join(dir_name, '/meet data')
    os.chdir(meet_data_path)
    with open(file_in) as file:
        #parse through file, find data and write to array
        #write by team ID. get team IDs from function get_team_from_id
        meet_data = []
        meet_name = file.readline()[:-1]
        for line in file:
            if is_int(line.split()[0]):
                meet_data.append([line[:-1]])
            else:
                #data in each non-event line is seperated by a comma
                linedata = line.split(',')
                name = linedata[0]
                team_id = linedata[1].split('=')[-1]
                time = linedata[2].split()[-1]
                #handle an error I got for a DQ I think
                if 'time:' in time:
                    #can't be 0 else score will be nutty
                    time = '99:99:59.99'
                #make sure correct event is appended
                current_index = len(meet_data) - 1
                #add the data from the line to the event array
                meet_data[current_index].append([name,team_id,time])
    os.chdir(dir_name)
    import score
    ranked_swims=[]
    #to look for team IDs -> is meet_data[event][1]
    all_team_ids = []
    for event in range(len(meet_data)):
        for swim in range(1,len(meet_data[event])):
            current_team_id = meet_data[event][swim][1]
            if current_team_id not in all_team_ids:
                #only add the team ID to list if you havent already
                all_team_ids.append(current_team_id)
    #create a list of all teams from ids
    all_teams = [get_team_from_id(t_id) for t_id in all_team_ids]
    #create dict of {id:teamname,...}
    team_dict = dict(zip(all_team_ids, all_teams))
    #look through each event, and find/rank best swims
    for event in range(len(meet_data)):
        #event data is stored in 0th index of each entry in meet_data array
        current_event = meet_data[event][0].rsplit(' ',1)[0]
        current_gender = meet_data[event][0].rsplit(' ',1)[1]
        if 'w' in current_gender.lower():
            current_gender = 'women'
        else:
            current_gender = 'men'
        #want to skip first index, since that is just the event
        for swim in range(1,len(meet_data[event])):
            current_swim = meet_data[event][swim]
            name = current_swim[0]
            team_id = current_swim[1]
            team_name = team_dict[team_id]
            time = current_swim[2]
            current_score = score.nscore(time, current_event, current_gender)
            ranked_swims.append((current_event, team_name, name, time, current_score))
    #sorts list from best score to worst score
    sorted_swims = sorted(ranked_swims, key = lambda x: x[4], reverse = True)
    return sorted_swims
