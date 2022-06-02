import sys
from functions import *
from reconstructionGraphingFunctions import *
"""
Run as:
    python3 generateGraphsForDataframe.py [inputFile]

This code is used to generate graphs for an input dataframe. Since I will likely
want to use this code for multiple purposes, I will start by making it general use,
outputting scatterplots first to an output directory. Then, you can take those
columns and build other things over top of those scatterplots. Eventually, would
be great to add in other types of graphs to graph that can just be input and created.

I will use this to input datafiles generate by other pieces of code that can then be
analyzed.
"""

#MAIN
# variables: if want to make this more multipurpose, add the below into a config file
#outputDir = '/mnt/c/Users/gjowl/github/Sequence-Design/ngsAnalysis/2022-5-13/graphs/'
outputDir = '/exports/home/gloiseau/github/Sequence-Design/ngsAnalysis/2022-5-13/graphs/'
columnsToAnalyze = ['Total']

# make the output directory if it doesn't exist
makeOutputDir(outputDir)

# read in input file from command line file options
inputFile = sys.argv[1]
df = pd.read_csv(inputFile)

# TODO: do this in my actual analysis file
gpaFluor = 109804.5
#df['Percent GpA'] = df['Average']/gpaFluor*100
#df['StdDev'] = df['StdDev']/gpaFluor*100

# get a list of dataframes of all sequences that are from the same design group (runNumber or StartSequence)
list_designDf = getListOfDfWithUniqueColumnVal(df, 'runNumber')

#TODO: I should convert these in the final alldata dataframe to actual names (energy score and fluorescence)
xAxis = 'Total'
#yAxis = 'Percent GpA' # Fluorescence
yAxis = 'Average' # Fluorescence

# replaces all values greater than 0 with 0
df.loc[df[xAxis] > 100, xAxis] = 0

getScatterplotsForDfList(list_designDf, 'runNumber', xAxis, yAxis, outputDir)
# TODO: add in a way to identify any sequences with the same positions for the interface
# I think take the interface, identify which positions are not dash, add that number to a list
# and if sequences match that list then add to dictionary? OR easier would be to go through all,
# get the sequences that match, output that dataframe, then continue from the first one that doesn't match
# that combo in a list of combos (and then it's probably easier to output all of those as dataframes list 
# rather than just converting dictionaries)
list_sameInterfaceDf = []
list_interface = []
for interface in df['Interface']:
    # identify positions of interface that aren't dash
    numInterface = []
    nInterface = 'x'
    i = 0
    for AA in interface:
        if AA != '-':
            index = interface.index(AA,i)
            #print(interface, AA, index)
            numInterface.append(index)
            nInterface = nInterface+str(index)
        i+=1
    list_interface.append(nInterface) 
df['numInterface'] = list_interface
list_interfaceDf = getListOfDfWithUniqueColumnVal(df, 'numInterface')
getScatterplotsForDfList(list_interfaceDf, 'numInterface', xAxis, yAxis, outputDir)
interfaceFile = outputDir+'interfaces.csv'
df.to_csv(interfaceFile)
exit()

# TODO: how do I get rid of things that don't seem to correlate...? What is a good way to cutoff data?
# Maybe looking at the counts per LB and M9 for some sequences?
# TODO: look at percent GpA and energy score differences to choose sequences to look at docking and backbone repacks:
# come up with some way to say that these numbers are too different?
# some way to show correlation +/- a value or so? as in like move down 10%: what is the energy score and what's a 
# reasonable acceptable range for that score


for interface in df['Interface']:
    for numInterface in list_interface:
        print(numInterface)
        for index in numInterface:
            if interface[index] == '-':
                print(index)

pattern = '^A....G$'
test_string = 'AGLLAG'
result = re.match(pattern, test_string)
if result:
  print("Search successful.")
else:
  print("Search unsuccessful.")	

pattern = '^a...s$'
test_string = 'abyss'
result = re.match(pattern, test_string)
if result:
  print("Search successful.")
else:
  print("Search unsuccessful.")	

# TODO: input data here for kde plotting; go through the xShifts and crossingAngles and such here for any
# generated dataframes