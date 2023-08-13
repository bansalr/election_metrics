import sys,os
import pandas as pd
import numpy as np
pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

## my own libs
extra_path = "/Users/rbansal/Dropbox/ElectionData/lib" # whatever it is
if extra_path not in sys.path:
    sys.path.append(extra_path)

from india_data import *
from indices import *

## lets load some data!!!

election_data = "/Users/rbansal/Dropbox/ElectionData"

kaggle_2019 = election_data + "/" + "kaggle/LS_2.0.csv"
bhavnani_2014 = election_data + "/" + "bhavnani/Bhavnani India national election dataset v 2.csv"
us_presidential = election_data + "/" + "mit_election_lab/US Presidential Election 1976-2020.csv"

ls_df = read_kaggle_and_bhavnani(kaggle_2019, bhavnani_2014)
calc_stats(ls_df)

us_df = read_us_data(us_presidential)


print("\n******Fixing State names****\n")
ls_df = fix_state_names (ls_df)
calc_stats(ls_df)
verify_states(ls_df)

print("\n******Fixing PC names****.....")
ls_df = fix_pc_names (ls_df)
calc_stats(ls_df)


