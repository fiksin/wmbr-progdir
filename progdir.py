import os
import csv
import numpy
import pprint
import pandas as pd

# create dataframe from spreadsheet containing members' volunteer ratings over past seasons
ratings_df = pd.read_csv('ratings.csv', index_col="Member")
labels = [x for x in ratings_df]

"""
labels = ['Affil', 'Show(s)', 'Summer-12', 'Fall-12', 'Spring-13', 'Summer-13', 'Fall-13', 
            'Spr-14', 'Sum-14', 'Fall-14', 'Spr-15', 'Sum-15', 'Fall-15', 'Spr-16', 
            'Sum-16', 'Fall-16', 'Spr-17', 'Sum-17', 'Fall-17', 'Spr-17.1', 'Sum-18', 
            'Avg Prev 3', 'Current Ratings', 
            'FIX', 'CALC AP3', 'CALC CURRENT']
"""

rating_labels = labels[2:-5]
"""
rating_labels = ['Summer-12', 'Fall-12', 'Spring-13', 'Summer-13', 'Fall-13', 
                    'Spr-14', 'Sum-14', 'Fall-14', 'Spr-15', 'Sum-15', 'Fall-15', 
                    'Spr-16', 'Sum-16', 'Fall-16', 'Spr-17', 'Sum-17', 'Fall-17', 
                    'Spr-17.1', 'Sum-18']
"""

ratings_df['Ratings List'] = ratings_df.values.tolist()
ratings_len = len(ratings_df["Show(s)"])

for i in range(ratings_len):
    i_ratings = []
    for label in rating_labels:
        rating = ratings_df.at[ratings_df.index[i], label]

        try:
            rating = float(rating)
            if not numpy.isnan(rating):
                i_ratings.append(rating)
        except ValueError:
            pass

    ratings_df.at[ratings_df.index[i], "Ratings List"] = i_ratings
    ratings_df.at[ratings_df.index[i], "Current Rating"] = i_ratings[-1] if len(i_ratings) > 0 else 2.9
    
    if len(i_ratings) == 0: # new member (no current season rating)
        new_val = 2.9
    elif len(i_ratings) in (1,2): # if only 1 previous season or no previous seasons, take previous season as avg
        new_val = i_ratings[0]
    elif len(i_ratings) == 3: # 2 previous seasons
        new_val = sum(i_ratings[0:2]) / 2.0
    else:
        new_val = sum(i_ratings[-4:-1]) / 3.0
    ratings_df.at[ratings_df.index[i], "Avg Prev 3"] = new_val

"""
Order by groups first using current ratings and avg previous 3
If 1: leave it
If they’re a 2: 1 if they want to keep their same show, 2 if not
Put the rest in by current ratings and then go in manually with avg previous 3
Check if anyone >=3 has a avg previous 3 of 1 or 2 and then use that

Order by: 
groups, current ratings (e.g. between group 1 and group 2 simultaneously or dip in ratings), 
OTA trained, previous 3, random (click in opposite order bc last selection is most important)
"""

# create dataframe from spreadsheet containing all proposals
prop_df = pd.read_csv('prop.csv')
prop_len = len(prop_df["Show"])

# make column of random numbers between 0-1
prop_df["Random"] = numpy.random.uniform(0.0, 1.0, prop_df.shape[0])
missed_members = []

# flip OTA boolean to prioritize OTA-trained (True) for sorting later
prop_df["OTA"] = ~prop_df["OTA"]

# problem to solve later: cohosts with different volunteering ratings
for i in range(prop_len):
    host = prop_df.at[prop_df.index[i], "Host 1"]
    group = prop_df.at[prop_df.index[i], "Group"]
    
    try:
        # set trended and current ratings in column to calculated values
        prop_df.at[prop_df.index[i], "trended ratings"] = ratings_df.loc[host]["Avg Prev 3"]
        prop_df.at[prop_df.index[i], "current rating"] = ratings_df.loc[host]["Current Rating"]
    
    except KeyError:
        # fix this later--currently operates as if hosts missing from ratings list are all new
        # problem is that members are sometimes listed by nickname on one list but not the other
        # could add a prompt for searching and correcting if host exists in list under another name
        # could also check by group number
        missed_members.append(host)
        prop_df.at[prop_df.index[i], "trended ratings"] = 2.9
        prop_df.at[prop_df.index[i], "current rating"] = 2.9

    # now correct groups: if group 2, change to 1 if they want to keep the same time slot
    if group == 2 and prop_df.at[prop_df.index[i], "Keep same slot?"] == "Yes":
        prop_df.at[prop_df.index[i], "Group"] = 1

    # if group 3 or greater, update group number if trended ratings correspond to group 1-2
    if group >= 3 and prop_df.at[prop_df.index[i], "trended ratings"] < 3:
        prop_df.at[prop_df.index[i], "Group"] = prop_df.at[prop_df.index[i], "trended ratings"]

prop_df = prop_df.sort_values(by=["Group", "current rating", "OTA", "trended ratings", "Random"])
prop_df["OTA"] = ~prop_df["OTA"] # flip OTA boolean back to OTA-trained=True for accurate representation

prop_df.to_csv("sorted.csv")
