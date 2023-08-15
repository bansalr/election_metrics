import pandas as pd
from pc_transforms import pc_transforms


def read_india_data(election_data):
    kaggle_2019 = election_data + "/" + "kaggle/LS_2.0.csv"
    bhavnani_2014 = election_data + "/" + "bhavnani/Bhavnani India national election dataset v 2.csv"

    ls_df = read_kaggle_and_bhavnani(kaggle_2019, bhavnani_2014)
    #calc_stats(ls_df)

    print("\n******Fixing State names****\n")
    ls_df = fix_state_names (ls_df)

    #calc_stats(ls_df)
    verify_states(ls_df)

    print("\n******Fixing PC names****.....")
    ls_df = fix_pc_names (ls_df)
    return ls_df

def read_us_data(election_data):

    CUTOFF_YEAR = 1900
    presidential_data_file_path = election_data + "/" + "mit_election_lab/US Presidential Election 1976-2020.csv"
    electors_data_file_path = election_data + "/" + "us_president_electors/electors.csv"

    # us_df = pd.read_csv(presidential_data_file_path)    
    # cols = [
    #     'year', ## year
    #     'state', ## ==> state_name
    #     'state_po', # n/a
    #     'state_fips', #n/a
    #     'state_cen', #n/a
    #     'state_ic', #n/a
    #     'office', #n/a
    #     'candidate', #n/a
    #     'party_detailed', # ==> party
    #     'writein',
    #     'candidatevotes', # ==> total_votes
    #     'totalvotes', # delete
    #     'version', # n/a
    #     'notes', #n/a 
    #     'party_simplified' #n/a
    #     ]
    # new_df = us_df.rename(columns={'state' : 'state_name',
    #                                'party_simplified' : 'party',
    #                                'totalvotes' : 'all_votes',
    #                                'candidatevotes' : 'total_votes'
    #                                })


    # new_df['max_polled'] = new_df.groupby(['state_name','party','year'])['total_votes'].transform('max')    
    # new_df['winner'] = new_df['max_polled'] == new_df['total_votes']

    electors_df = pd.read_csv(electors_data_file_path)    
    electors_df['year'] = electors_df.Year.str.split(' - ').str[0].astype(int)
    electors_df['winner'] = electors_df.Year.str.split(' - ').str[1]

    ## trim to CUTOFF_YEAR+
    electors_df = electors_df[electors_df.year > CUTOFF_YEAR]

    electors_df = electors_df.rename(columns={'total': 'total_votes',
                                              'EV.3' : 'EV.4',
                                              'EV.2' : 'EV.3',
                                              'EV.1' : 'EV.2',
                                              'EV' : 'EV.1',
                                              'State' : 'state_name',
                                              })
    
    # thurmond
    # electors_df.loc[((electors_df.winner == "Truman") & (electors_df.Party == "Other")),"Party"] = "Democratic"

    # wallace
    #electors_df.loc[((electors_df.winner == "Nixon") & (electors_df.Party == "Other")),"Party"] = "Republican"

    electors_df.loc[(electors_df.year == 1960) & (electors_df.state_name=='Mississippi'),'EV.1'] = 0
    electors_df.loc[(electors_df.year == 1960) & (electors_df.state_name=='Mississippi'),'EV.2'] = 0

    electors_df['EV.1'] = electors_df['EV.1'].str.strip("*").astype(float)
    electors_df['EV.2'] = electors_df['EV.2'].str.strip("*").astype(float)
    
    electors_df.loc[electors_df['EV.1'].isna(),'EV.1'] = electors_df.loc[electors_df['EV.1'].isna(),'EV.2']

    
    #mport pdb;pdb.set_trace()    
    #electors_df.loc[electors_df.EV.isna(),'EV'] = electors_df.loc[electors_df.EV.isna(),'EV.2']    

    for party in electors_df[electors_df.year > CUTOFF_YEAR].Party.unique().tolist():
        electors_df[party+"_ev"] = 0
        electors_df[party+"_votes"] = 0

    def map_votes_evs(row):
        # for each row first who won
        # greater votes and share
        max_votes = max(row['party.1'], row['party.2'])
        min_votes = min(row['party.1'], row['party.2'])
        
        if row.Party == 'Republican':
            row["Republican_ev"] = row['EV.1']
            row["Republican_votes"] = max_votes
            row["Democratic_ev"] = 0
            row["Democratic_votes"] = min_votes
            
        if row.Party == 'Democratic':
            row["Democratic_ev"] = row['EV.1']
            row["Democratic_votes"] = max_votes

            row["Republican_ev"] = 0
            row["Republican_votes"] = min_votes

        return row
    
    new_elector_df = electors_df.apply(lambda row: map_votes_evs(row), axis=1)
    new_elector_df['Other_votes'] = new_elector_df.total_votes - (new_elector_df.Republican_votes + new_elector_df.Democratic_votes)

    elector_df_summed = new_elector_df.groupby('year').sum(['Democratic_ev','Democratic_votes','Republican_ev','Republican_votes']).reset_index()
    return elector_df_summed

def read_kaggle_and_bhavnani(kaggle_2019, bhavnani_2014):
    kaggle_2019_df = pd.read_csv(kaggle_2019)
    bhavnani_2014_df = pd.read_csv(bhavnani_2014,index_col="linenum")

    ## add missing columns
    kaggle_2019_df['year'] = 2019

    ## calculate bhavnani winner column
    bhavnani_2014_df['winner'] = 0
    bhavnani_2014_df['max_polled'] = bhavnani_2014_df.groupby(['state_name','pc','year'])['total_votes'].transform('max')
    bhavnani_2014_df['winner'] = bhavnani_2014_df['max_polled'] == bhavnani_2014_df['total_votes']
    bhavnani_2014_df['winner'] = bhavnani_2014_df['winner'].astype(int)
    subselect_columns =  {
    
    'bhavnani_2014_df_columns' : [  'state_name', 
                                    'year', 
                                    'pc',
                                    'candidate_name', 
                                    'gender',
                                    'winner',  ## calc
                                  'party', 
                                  'total_votes', 
                                  'total_electors'],

    'kaggle_2019_df_columns' : ['state_name', 
                                'year', 
                                'pc', 
                                'candidate_name', 
                                'gender',
                                'winner',  ## calc
                                'party', 
                               'total_votes',
                               'total_electors']
    }

    ls_df = pd.concat([bhavnani_2014_df[subselect_columns['bhavnani_2014_df_columns']], 
                      kaggle_2019_df[subselect_columns['kaggle_2019_df_columns']]])

    ## lets make sure we got it right:
    print(f" bhavnani_df: {bhavnani_2014_df.shape}\n kaggle_2019_df: {kaggle_2019_df.shape}\n ls_df: {ls_df.shape}\n")
    assert ls_df.shape[0] == (bhavnani_2014_df.shape[0] + kaggle_2019_df.shape[0]), "Shape Check failed"

    ls_df['state_name'] = ls_df['state_name'].str.lower()
    ls_df['pc'] = ls_df['pc'].str.lower()
    ls_df['pc'] = ls_df['pc'].str.strip()

    return ls_df

def fix_state_names (ls_df):
    ## Fix Delhi
    ls_df.loc[ls_df.state_name.str.contains("delhi"), 'state_name'] = "nct delhi"

    ## Fix pondicherry --> puducherry
    ls_df.loc[ls_df.state_name.str.contains("pondicherry"),'state_name'] = "puducherry"

    ## Fix chhattisgarh --> chattisgarh
    ls_df.loc[ls_df.state_name.str.contains('chhattisgarh'),'state_name'] = 'chattisgarh'

    ## fix uttaranchal --> uttarakhand
    ls_df.loc[ls_df.state_name.str.contains('uttaranchal'),'state_name'] = 'uttarakhand'


    ## daman and diu were with goa and then separates when goa became a state
    ## and then merged with diu and nagar haveli so we will treat all of them as one
    ## and create a unit called goa, diu and daman and nagar haveli - of Goa et al for short.
    ls_df.loc[ls_df.state_name.str.contains("goa"),'state_name'] = "goa et al"
    ls_df.loc[ls_df.state_name.str.contains("daman & diu"),'state_name'] = "goa et al"
    ls_df.loc[ls_df.state_name.str.contains("haveli"),'state_name'] = "goa et al"
    ls_df.loc[ls_df.state_name.str.contains('orissa'),'state_name'] = 'odisha'

    ## Fix Telangana by transferring its constituencies from AP
    ## Fix Uttarakhand by transferring its constituences back from UP?

    return ls_df

def verify_states(ls_df):
    ## Sanity checks
    
    ## we are missing ladakh but no elections have been held since the separation
    ## and we are missing daman and dadra 
    ## as of 2023 there are 28 states + 8 Union teritories. so we should have 36 but -ladakh and -daman/dadra we should have 34
    assert ls_df['state_name'].nunique() == 34, "Number of states/uts should be 34"
    
    print(f"\n\nStates/UTs:\n{ls_df['state_name'].unique()}\n\nNum states: {ls_df['state_name'].nunique()}\n")
    

def fix_pc_names (ls_df):
    for state,transforms in pc_transforms.items():
        for old_pc, new_pc in transforms.items():
            #print(state,old_pc,new_pc)
            ls_df.loc[(ls_df.state_name == state) & (ls_df.pc==old_pc),'pc']= new_pc
    return ls_df

def calc_stats (ls_df):

    ## first calculate for across pc - parliamentary constituency - how many years they have
    num_years = len(ls_df.year.unique().tolist())
    state_pc_group = ls_df[ls_df.winner == 1].groupby(['state_name','pc'])
    for year in range(1,num_years+1):
        num_pcs = (state_pc_group.year.count() == year).sum()
        print(f"PC with {year}:{num_pcs}")

    print("\n")
    
    ## then for reach ls year, calculate how many pcs there are 
    ls_years = ls_df[ls_df.winner==1].year.unique().tolist()
    for ls_year in ls_years:
        print(f"PC for LS Year: {ls_year}: {(ls_df[ls_df.winner ==1].year == ls_year).sum()}")


