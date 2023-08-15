import concentrationMetrics as cm
import pandas as pd

import numpy as np
import math

def gallagher (votes, seats):
    assert len(votes) == len(seats), f"lengths not equal: {len(votes)} != {len(seats)}"
    
    return math.sqrt((((100.*votes/votes.sum())-(100.*seats/seats.sum()))**2).sum()/2)


def calc_indices_us (data_df):

    measures = {
        'year' : [],
        'total_votes': {
            'hhi' :[],
            'enp':[],
            'shannon':[],
            'simpson':[],
        },
        'electors' : {
            'hhi' :[],
            'enp':[],
            'shannon':[],
            'simpson':[],
        },
        'gallagher': [],
    }
    
    myIndex = cm.Index()

    portfolios = []
    election_years = data_df.year.unique()
    metric_columns = {
        'electors': ['Democratic_ev', 'Republican_ev', 'Other_ev'],
        'total_votes' : ['Democratic_votes', 'Republican_votes','Other_votes']
    }
    
    for election_year in election_years:
        
        portfolio = data_df[data_df.year==election_year][['Democratic_ev', 'Republican_ev', 'Other_ev', 'Democratic_votes', 'Republican_votes','Other_votes']]
        
        measures['year'].append(election_year)
        for metric in ['total_votes','electors']:
            #import pdb;pdb.set_trace()            
            measures[metric]['hhi'].append(myIndex.hhi(portfolio[metric_columns[metric]].values[0]))
            measures[metric]['enp'].append(1.0/myIndex.hhi(portfolio[metric_columns[metric]].values[0]))
            measures[metric]['shannon'].append(myIndex.shannon(portfolio[metric_columns[metric]].values[0]))
            measures[metric]['simpson'].append(myIndex.simpson(portfolio[metric_columns[metric]].values[0]))

        portfolio['year'] = election_year
        portfolios.append(portfolio)
                         
        ## now lets do gallagher
        measures['gallagher'].append(gallagher(votes=portfolio[metric_columns['total_votes']].values,
                                               seats=portfolio[metric_columns['electors']].values))

    raw_df = pd.concat(portfolios)
    return {'measures': measures,
            'raw' : raw_df
            }

def calc_indices_india (data_df):

    measures = {
        'year' : [],
        'total_votes': {
            'hhi' :[],
            'enp':[],
            'shannon':[],
            'simpson':[],
        },
        'seats' : {
            'hhi' :[],
            'enp':[],
            'shannon':[],
            'simpson':[],
        },
        'gallagher': [],
    }
    raw_data = {
        'year' : [],
        'seats_party_counts' : [],
        'total_votes_party_counts' : [],        
        'seats' : [],
        'voteshare': [],
    }
    
    myIndex = cm.Index()

    total_votes_df = data_df.groupby(['year','party']).total_votes.sum().reset_index()
    portfolios = []
    election_years = data_df.year.unique()
    
    for election_year in election_years:
        votes_df = total_votes_df[total_votes_df.year==election_year][['party','total_votes']].set_index('party')
        seats_series = data_df[(data_df.winner==1) & (data_df.year==election_year)].groupby(['party'])['party'].count()
        seats_series.index.name = 'seats'
        seats_series.name = 'seats'
        
        portfolio = pd.concat([votes_df, seats_series], axis=1)
        portfolio.loc[(portfolio.seats.isna()),'seats'] = 0

        
        measures['year'].append(election_year)
        for metric in ['total_votes','seats']:
            measures[metric]['hhi'].append(myIndex.hhi(portfolio[metric].values))
            measures[metric]['enp'].append(1.0/myIndex.hhi(portfolio[metric].values))
            measures[metric]['shannon'].append(myIndex.shannon(portfolio[metric].values))
            measures[metric]['simpson'].append(myIndex.simpson(portfolio[metric].values))

        portfolio['year'] = election_year
        portfolios.append(portfolio)
                         
        ## now lets do gallagher
        measures['gallagher'].append(gallagher(votes=portfolio['total_votes'].values,
                                               seats=portfolio['seats'].values))

    raw_df = pd.concat(portfolios)
    return {'measures': measures,
            'raw' : raw_df
            }


