import concentrationMetrics as cm
import pandas as pd

import matplotlib.pyplot as plt
from plotnine import ggplot, aes, facet_grid, labs, geom_point, geom_line, theme, element_blank
import numpy as np
import math

def gallagher (votes, seats):
    assert len(votes) == len(seats), f"lengths not equal: {len(votes)} != {len(seats)}"
    
    return math.sqrt((((100.*votes/votes.sum())-(100.*seats/seats.sum()))**2).sum()/2)

def calc_indices (data_df):


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


def plot_indices(indices_df,plot_title_enp, plot_title_measure):
    "Lok Sabha Seat Share: Effective Number of Parties 1977-2019"

    #plt.style.use(['dark_background', 'ggplot'])
    #plt.title('HHI for India LS 1977-2019')
    #plt.xlabel('LS Year')
    #plt.ylabel('Herfindahl-Hirschman Index')
    #plt.scatter(ls_years, hhi)
    #plt.show()
    
    #plt.style.use(['dark_background', 'ggplot'])
    #plt.style.use('fivethirtyeight')
    
    #plt.xlabel('Lok Sabha Election Year')
    #plt.ylabel('Effective Number of Parties')
    #plt.scatter(ls_years, enp)
    #plt.title('Effective Number of Parties for LS 1977-2019')
    
    #plt.show()
    
    g1 = ggplot(indices_df, aes(x='year', y='enp')) + \
        labs(title=plot_title_enp) + \
        geom_line() + \
        geom_point(colour = "red", size = 3,alpha=0.4)
    
    indices_melt = indices_df.melt(id_vars=['year'], value_vars=['hhi','simpson',"shannon","enp"], var_name='legend', value_name='a_or_b')

    g2 = ggplot(indices_melt, aes(x='year', y='a_or_b')) + geom_point(size=3,alpha=0.05) + \
        geom_line(aes(color='legend')) + \
        labs(y="", x="Lok Sabha Election Year",title=plot_title_measure) + theme(legend_title=element_blank())
    return [g1,g2]
