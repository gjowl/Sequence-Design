'''
File: /home/loiseau@ad.wisc.edu/github/Sequence-Design/ngsReconstruction/CHIP2_analysisCode/compareSequencingPerSegment.py
Project: /home/loiseau@ad.wisc.edu/github/Sequence-Design/ngsReconstruction/CHIP2_analysisCode
Created Date: Tuesday September 5th 2023
Author: loiseau
-----
Last Modified: Tuesday September 5th 2023 12:49:01 pm
Modified By: loiseau
-----
Description:
Used to compare sequencing data between LB and sorts. 

To run: python3 lb_file sort_file 
Files I used in my runs: lb_file = CHIP2/analyzedData/maltoseTest/LBPercents.csv
 sort_file = CHIP2/analyzedData/reconstruction_by_percent/avgFluorGoodSeqs.csv)
Output: lb_file_noZero.csv and sort_file_noZero.csv in the same directory as the input files

Hardcode: segments to compare; change these to the segments of interest
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

import os, sys, pandas as pd

# read in the command line arguments
lb_file = sys.argv[1]
sort_file = sys.argv[2]

# read in the input files
df_lb = pd.read_csv(lb_file)
df_sort = pd.read_csv(sort_file)

# segments to compare
segments = ["13", "18"]

# keep the sequences that have the same segments
df_lb = df_lb[df_lb['Segments'].isin(segments)]
df_sort = df_sort[df_sort['Segments'].isin(segments)]

# remove sequences where the data (after the segments column) has at least one 0
df_lb = df_lb.loc[(df_lb.iloc[:, 1:] != 0).all(axis=1)]
df_sort = df_sort.loc[(df_sort.iloc[:, 1:] != 0).all(axis=1)]
df_lb.to_csv(f'{lb_file[:-4]}_noZero.csv', index=False)
df_sort.to_csv(f'{sort_file[:-4]}_noZero.csv', index=False)
