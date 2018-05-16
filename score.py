import math

def american_record(event,gender = 'men'):
    events = ['50 Free','100 Free','200 Free','500 Free','1000 Free','1650 Free',
              '100 Back','200 Back','100 Breast','200 Breast','100 Fly','200 Fly',
              '200 IM','400 IM','200 Free Relay','400 Free Relay','800 Free Relay',
              '200 Medley Relay','400 Medley Relay']
    times_men = [17.63,39.9,89.5,247.25,513.93,858.25,43.49,95.73,49.69,107.91,
                 42.8,97.35,98.13,213.42,0,0,0,0,0]
    times_women = [21.12,45.56,99.1,264.06,539.65,903.31,49.69,107.3,56.25,122.6,
                   49.43,109.51,110.67,234.6,0,0,0,0,0]
    for i in range(len(events)):
        if events[i] == event:
            if gender == 'men':
                return times_men[i]
            else:
                return times_women[i]
            
def big_8th(event,gender='men'):
    events = ['50 Free','100 Free','200 Free','500 Free','1000 Free','1650 Free',
              '100 Back','200 Back','100 Breast','200 Breast','100 Fly','200 Fly',
              '200 IM','400 IM','200 Free Relay','400 Free Relay','800 Free Relay',
              '200 Medley Relay','400 Medley Relay']
    times_men = [19.59,43.09,95.46,(4*60+19),0,(15*60+6.88),47.02,102.99,52.9,
                 115.9,46.37,104.6,104.24,(3*60+47.62),0,0,0,0,0]
    times_women = [22.42,49.12,105.57,(4*60+40.73),0,(16*60+11.92),52.6,114.65,
                   60.47,131.41,53.06,116.91,117.45,(4*60+11.05),0,0,0,0,0]
    for i in range(len(events)):
        if events[i] == event:
            if gender == 'men':
                return times_men[i]
            else:
                return times_women[i]
            
#basically just making a piecwise function defined by a line in pt slope form
            
def score_function(threshold, record, time):
    if time == '–':
        return 0
    try:
        if time > threshold + record:
            return 0
    except TypeError:
        time = time_type_convert(time)
        if time > threshold + record:
            return 0
    slope = float(-1000/threshold)
    score = 1000*math.pow((slope*(time - (threshold+record))/1000),1.75)
    return int(score)
#compare time to american record
#score should be 0 until some threshold, then scale to record for max of 1k
def nscore(time, event, gender='men'):
    dist = int(event.split()[0])
    record = american_record(event,gender)
    threshold = int((1/10)*dist) #can adjust this, but now is 5sec/50
    score = score_function(threshold, record, time)
    return score

def cscore(time, event, gender='men'):
    dist = int(event.split()[0])
    record = big_8th(event,gender)
    threshold = int((1/10)*dist) #can adjust this, but now is 5sec/50
    score = score_function(threshold, record, time)
    return score

def seconds_convert(t):
    minutes = int(t/60)
    hours = int(minutes/60)
    minutes = minutes%60
    seconds = int(t - hours*60*60 - minutes*60)
    time = str(hours)+'h'+str(minutes)+'m'+str(seconds)+'s'
    return time

def time_type_convert(time):
    try:
        timesp = time.split(':')
    except AttributeError:
        return time
    if len(timesp)==1:
        time = float(timesp[0])
    elif len(timesp)==2:
        time = float(timesp[1]) + 60*float(timesp[0])
    elif len(timesp)==3:
        time = float(timesp[2]) + 60*float(timesp[1]) + 60*60*float(timesp[1])
    else:
        return
    return time

#input should be list of best times by year, most recent first
def impScore(time_list):
    #want to take percent improved between each year, weighted average of those
    percent_list = []
    for index in range(0,len(time_list)-1):
        percent = (time_list[index+1] - time_list[index])/time_list[index+1]
        percent_list.append(percent)
    weight = 0
    for index in range(len(percent_list)):
        weight = weight + percent_list[index]*(len(percent_list)-index)
    weight = weight/(len(percent_list)*(len(percent_list)-1)/2)
    return int(10000*weight)
