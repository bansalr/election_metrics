import pandas as pd
from pc_transforms import pc_transforms


def read_us_data(file_path):
    us_df = pd.read_csv(file_path)
    cols = [
        'year', ## year
        'state', ## state_name
        'state_po', # n/a
        'state_fips', #n/a
        'state_cen', #n/a
        'state_ic', #n/a
        'office', #n/a
        'candidate', #n/a
        'party_detailed', # party
        'writein',
        'candidatevotes', # total_votes
        'totalvotes', # delete
        'version', # n/a
        'notes', #n/a 
        'party_simplified' #n/a
        ]
    return us_df


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


