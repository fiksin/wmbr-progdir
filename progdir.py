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
