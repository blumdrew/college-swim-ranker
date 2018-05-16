from splinter import Browser
import time
import re

#--This file is responsible for the heavy lifting of looking through site--
#--------www.collegeswimming.com and attempting to gather meet data--------
#NOTE executable_path should be changed to reflect where chromedriver is 
#installed for whomever the user is

seasons_list = ['2017-2018','2016-2017','2015-2016','2014-2015','2013-2014',
                '2012-2013','2011-2012','2010-2011','2009-2010','2008-2009']
def test_letters(string):
    #use to test what is in a string, returns false if no letters
    match = re.search('[a-zA-Z]',string)
    if match is None:
        return False
    else:
        return True

def find_number_of_events(url):
    #url is just the url for some meet on collegeswimming
    executable_path = {'executable_path':'/Users/andrewlindstrom/Documents/chromedriver'}
    browser = Browser('chrome',headless=True,**executable_path)
    #path below is xml path to find how many events are in some meet
    event_path = '/html/body/div/div/div/div/div/div/section/div/div/div/ul/li/a/div/div'
    browser.visit(url)
    event_browser = browser.find_by_xpath(event_path)
    if len(event_browser) > 0:
        #gets the final event for whatever the meet is
        last_event_no = event_browser[len(event_browser) - 2].text
        if last_event_no != '':
            browser.quit()
            return int(last_event_no)
        else:
            browser.quit()
            return 21
    else:
        browser.quit()
        return 21

def meet_name(url):
    executable_path = {'executable_path':'/Users/andrewlindstrom/Documents/chromedriver'}
    browser = Browser('chrome',headless=True,**executable_path)
    #path below is xml path to find name of the meet
    name_path = '/html/body/div/div/div/div/div/div/div/div/div'
    browser.visit(url)
    if len(browser.find_by_xpath(name_path)) != 0:
        meet = browser.find_by_xpath(name_path)[0].text
        browser.quit()
        #want to return plaintext of meet name, dont need extra \n in there
        return str(meet.split('\n')[0])
    else:
        browser.quit()
        #return empty string if no name is found - could be url error
        return ''

def meet_date(url):
    executable_path = {'executable_path':'/Users/andrewlindstrom/Documents/chromedriver'}
    browser = Browser('chrome',headless=True,**executable_path)
    #path below is xml path to find date of meet (as a string)
    date_path = '/html/body/div/div/div/div/div/div/div/ul/li'
    browser.visit(url)
    date_browser = browser.find_by_xpath(date_path)
    if len(browser.find_by_xpath(date_path)) != 0:
        date = date_browser[0].text.split('\n')[1]
        browser.quit()
        return date
    else:
        return ''
    

def get_team_ids(url):
    executable_path = {'executable_path':'/Users/andrewlindstrom/Documents/chromedriver'}
    browser = Browser('chrome',headless=True,**executable_path)
    #path below is xml path to find all the teams on a page
    team_path = '/html/body/div/div/div/div/div/div/div/div/div/table/tbody/tr/td/a'
    browser.visit(url)
    browser_data = browser.find_by_xpath(team_path)
    all_ids = []
    for entry in range(len(browser_data)):
        id_value = 0
        if entry % 2 == 1:
            #find team id from last part of link
            id_value = browser_data[entry]['href'].split('/')[-1]
            all_ids.append(id_value)
    browser.quit()
    return all_ids

#this function is essentially identical to the prior one, only difference is no
#mod2. This is just because of the way that the site is set up on relays vs. individuals
def get_relay_ids(url):
    executable_path = {'executable_path':'/Users/andrewlindstrom/Documents/chromedriver'}
    browser = Browser('chrome',headless=True,**executable_path)
    team_path = '/html/body/div/div/div/div/div/div/div/div/div/table/tbody/tr/td/a'
    browser.visit(url)
    browser_data = browser.find_by_xpath(team_path)
    all_ids=[]
    for entry in range(len(browser_data)):
        id_value = browser_data[entry]['href'].split('/')[-1]
        all_ids.append(id_value)
    browser.quit()
    return all_ids

#gets data from meet as [[event,[swimmer,teamID,time],[swimmer2..]],[event2,..]]
#Default event is Mens D1 NCAAS 2018 - thats the test meet
def cs_getdata(meet_id = '104736'):
    executable_path = {'executable_path':'/Users/andrewlindstrom/Documents/chromedriver'}
    browser = Browser('chrome',headless=True,**executable_path)
    start = time.time()
    url = 'https://www.collegeswimming.com/results/%s/event/%s/' %(str(meet_id),'%s')
    all_swims = []
    num_events = find_number_of_events(url% '1')
    meet = meet_name(url %'1')
    date = meet_date(url %'1')
    print('Getting swims from ' + meet)
    print('On ' + date)
    for i in range(1,num_events+1): #need to visit each event
        ltimes = []
        lnames = []
        browser.visit(url %str(i))
        #this path finds the data on the page, but should have length of at least 4
        #finds more than just the data needed
        path = '/html/body/div/div/div/div/div/div/div'
        browser_result = browser.find_by_xpath(path)
        #if browser_result is too short, break. no results on page or something went wrong
        if len(browser_result) < 4:
            break
        string_list = browser.find_by_xpath(path)[3].text.split('\n')
        #check to make sure there actually are results--the text is result
        if 'RESULT FILE HAS NOT BEEN SUBMITTED YET!' in string_list[0]:
            print('No results found')
            break
        #Remove %improvent, dont care about that. Part of the text found.
        for item in range(len(string_list)):
            if item + 1 > len(string_list):
                break
            elif '%' in string_list[item]:
                del(string_list[item])
        for item in range(len(string_list)):
            #Test to see if there are letters in the particular entry
            #add to times array if no, else add to names
            if test_letters(string_list[item]) == False:
                ltimes.append(string_list[item])
            else:
                lnames.append(string_list[item])
        #for relays -> ltimes contains all times, prelim and finals.
        #           -> lnames contains names + some extra parts, want to get rid of that
        #for individuals -> ltimes is either blank or just a few entries
        event_name = lnames[0]
        all_swims.append([event_name])
        #Need to distinguish between Relays and Individuals, because of website format
        if 'Relay' not in event_name:
            lteamIDs = get_team_ids(url %str(i))
        else:
            lteamIDs = get_relay_ids(url %str(i))
        
        del(lnames[0]) #Remove event name from that array, has been stored
        
        if len(ltimes) != 0: #reset ltimes for individual events
            if ltimes[0] == '–':
                ltimes = []
                
        to_del = []
        for item in range(len(lnames)):
            #iterate thru lnames to find items to remove. 
            if item + 1 > len(lnames):
                break
            elif lnames[item]=='A Final':
                to_del.append(item)
            elif lnames[item][:5]=='Rank ':
                to_del.append(item)
            elif lnames[item]=='B Final':
                to_del.append(item)
            elif lnames[item]=='Preliminaries':
                to_del.append(item)
            elif lnames[item]=='Relay Names':
                to_del.append(item)
            elif lnames[item]=='Finals':
                to_del.append(item)
            elif lnames[item]=='C Final':
                to_del.append(item)
        #remove things to be deleted from back of list, to make sure index is not
        #moved out of place
        for item in reversed(range(len(to_del))):
            del(lnames[to_del[item]])
            
        #for all individual events -> want to split string from [place],[name],[time]
        #and then write time to ltimes, and replace lname entry with just name

        #LOOK OVER THIS PART AGAIN SEEMS REALLY SLOPPY AND I CANT FOLLOW HAHA
        lnames_dummy = []
        if len(ltimes) == 0:
            for j in range(len(lnames)):
                current_entry = lnames[j].split()
                name = ''
                for k in range(1,len(current_entry)):
                    if test_letters(current_entry[k])==False:
                    #no letters -> time (note the loop starts at 1 = ignore first entry(always place)
                        ltimes.append(current_entry[k])
                    else:
                        name = name + current_entry[k] + ' '
                    if k + 1 == len(current_entry):
                        lnames_dummy.append(name.strip())
        else:
            for j in range(len(lnames)):
                current_entry = lnames[j].split()
                name = ''
                for k in range(1,len(current_entry)):
                    name = name + current_entry[k] + ' '
                    if k + 1 == len(current_entry):
                        lnames_dummy.append(name.strip())            
        lnames = lnames_dummy
        
        #remove extra 'PB's that may be in the list for some dumb reason
        to_del = []
        if len(lnames) != len(ltimes):
            for item in range(len(lnames)):
                if item + 1 == len(lnames):
                    break
                elif lnames[item]=='PB':
                    to_del.append(item)
        #same deal as before with reversed loop, making sure to preserve index
        for j in reversed(range(len(to_del))):
            del(lnames[to_del[j]])    
        if 'Diving' not in event_name:
            for j in range(len(ltimes)):
                #the messy error handling is messy, but sometimes the all_swims list
                #doesnt append for no reason. So try twice, then just add on 0s otherwise
                #should maybe find a better solution somehow
                try:
                    all_swims[i-1].append([lnames[j],lteamIDs[j],ltimes[j]])
                except IndexError:
                    try:
                        all_swims[i-1].append([lnames[j],lteamIDs[j],ltimes[j]])
                    except IndexError:
                        all_swims[i-1].append([0,0,0])
            print('Got results for ' + event_name)
    end = time.time()
    print('Took ' + str(int(end-start)) +'s')
    browser.quit()
    return all_swims

#Function to sort meet data by teamID
def sort_list(meet_data):
    by_teamID = []
    #first loops find all teams in meet, create first part of list 
    #[[id,name],[id2,name2],....]
    for event in range(len(meet_data)):
        for swim in range(len(meet_data[event])):
            current_teamID = meet_data[event][swim][1]
            team_bool = False
            for team in range(len(by_teamID)):
                if by_teamID[team][0] == current_teamID:
                    team_bool = True
                    break
            if team_bool == False:
                team_name = get_teamID(current_teamID)
                if team_name != None:
                    by_teamID.append([current_teamID,team_name,[]])
    #now, get data from the meet and add it to each teams list
    #final list should be [[id,team,[[event1,swim1,time1,swim2,time2,..],[event2..]],..]
    for event in range(len(meet_data)):
        current_event = meet_data[event][0]
        for swim in range(len(meet_data[event])):
            current_swimmer = meet_data[event][swim][0]
            current_teamID = meet_data[event][swim][1]
            current_time = meet_data[event][swim][2]
            #add all swam events for each team to list
            for team in range(len(by_teamID)):
                if current_teamID == by_teamID[team][0]:
                    event_bool = False
                    for swam_event in range(len(by_teamID[team][2])):
                        if by_teamID[team][2][swam_event][0] == current_event:
                            event_bool = True
                    if event_bool == False:
                        by_teamID[team][2].append([current_event])
    #now finally, add the swim data to the list
    for event in range(len(meet_data)):
        current_event = meet_data[event][0]
        for swim in range(len(meet_data[event])):
            current_swimmer = meet_data[event][swim][0]
            current_teamID = meet_data[event][swim][1]
            current_time = meet_data[event][swim][2]
            for team in range(len(by_teamID)):
                if by_teamID[team][0] == current_teamID:
                    for events in range(len(by_teamID[team][2])):
                        if current_event == by_teamID[team][2][events][0]:
                            by_teamID[team][2][events].append(current_swimmer)
                            by_teamID[team][2][events].append(current_time)
    return by_teamID
def max_pages(season):
    if season == '2017-2018':
        return 87
    elif season == '2016-2017':
        return 74
    elif season == '2015-2016':
        return 77
    elif season == '2014-2015':
        return 78
    elif season == '2013-2014':
        return 78
    elif season == '2012-2013':
        return 74
    elif season == '2011-2012':
        return 62
    elif season == '2010-2011':
        return 61
    elif season == '2009-2010':
        return 38
    else:
        return 1
def write_urls(season='2017-2018',file_out='urls'):
    executable_path = {'executable_path':'/Users/andrewlindstrom/Documents/chromedriver'}
    browser = Browser('chrome',headless=True,**executable_path)
    start = time.time()
    file_out = file_out + ' ' + season
    if file_out[-4:] != '.txt':
        file_out = file_out + '.txt'
    link_path = '/html/body/div/div/div/section/div/div/div/table/tbody/tr/td/a'
    page_url = 'https://www.collegeswimming.com/results/?season=%s&page=%s'
    last_page = max_pages(season)
    with open(file_out,'w') as out:
        for page in range(1,last_page+1):
            browser.visit(page_url %(season,str(page)))
            links = browser.find_by_xpath(link_path)
            for element in range(len(links)):
                out.write(links[element].text + ' ID=')
                id_split = links[element]['href'].split('/')[-1] #choose just the last part(id of meet)
                out.write(id_split + '\n')
            print('Page #'+str(page)+' written to '+file_out)
        
    end = time.time()
    browser.quit()
    return str('Finished in ' + str(int(end-start)) + 's')

def write_names_by_id(file_out='team ids.txt'):
    executable_path = {'executable_path':'/Users/andrewlindstrom/Documents/chromedriver'}
    browser = Browser('chrome',headless=True,**executable_path)
    start = time.time()
    team_url = 'https://www.collegeswimming.com/team/%s/'
    team_name_path = '/html/body/div/div/div/div/div/div/div/h1/a'
    max_team_id = 655 #looks like 656 is starting high schools... can add those later
    with open(file_out,'a') as out:
        for team_id in range(1,max_team_id+1):
            browser.visit(team_url %str(team_id))
            team_name_data = browser.find_by_xpath(team_name_path)
            if len(team_name_data)>0:
                team_name = team_name_data[0].text
                out.write(str(team_name) + ' ID=' + str(team_id) + '\n')
                print(str(team_name) + ' ID=' + str(team_id))
    end = time.time()
    browser.quit()
    return 'Finished in ' + str(int(end-start)) + 's'

#This file should take in return from cs_getdata() and write it to file                  
def write_results(results,meet_name,file_out='dump.txt'):
    with open(file_out,'w') as out:
        #Go through each event
        out.write(meet_name+'\n')
        for event in range(len(results)):
            event_title = results[event][0]
            out.write(event_title+'\n')
            if 'Diving' not in event_title:
                for details in range(1,len(results[event])):
                    name = results[event][details][0]
                    teamID = results[event][details][1]
                    time = results[event][details][2]
                    to_print = str(name)+', teamID='+str(teamID)+', time: '+str(time)
                    to_print = str(to_print.encode('ascii','ignore'))[2:][:-1]
                    out.write(to_print + '\n')
            
                    
def get_teamID(teamID):
    try:
        id_file = open('team ids.txt')
    except FileNotFoundError:
        print('File Not Found, writing IDs to txt file')
        write_names_by_id()
        id_file = open('team ids.txt')
        
    for line in id_file:
        currentID = line.split('=')[1][:-1]
        current_team = line.split('=')[0][:-3]
        if currentID == str(teamID):
            id_file.close()
            return current_team
