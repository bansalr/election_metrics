import sys,os
import pandas as pd
import numpy as np
pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


## my own libs
extra_path = "/Users/rbansal/src/election_metrics/lib" # whatever it is
if extra_path not in sys.path:
    sys.path.append(extra_path)

from india_data import *
from indices import *
from plot_metrics import *

## lets load some data!!!

election_data = "/Users/rbansal/src/election_metrics/data/"
us_pres_df = read_us_data(election_data)
india_loksabha_df = read_india_data(election_data)

## run the calculations
india_outputs = calc_indices_india(india_loksabha_df)
us_outputs = calc_indices_us(us_pres_df)

