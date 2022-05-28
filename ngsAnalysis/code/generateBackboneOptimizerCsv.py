import sys
from functions import *

"""
Run as:
    python3 generateBackboneOptimizerCsv.py [energyFile]

This converts a dataframe of energy files for my designed sequences into a 
csv file that can be used to run a local condor submit job on our server
to optimize backbone structures. When I generated mutants for my designs,
I had trouble writing a script that would quickly run this backbone optimization
on every mutant, so I just made a mutation on an optimized backbone of the design
sequence, and then calculated the energy for the mutant. The energies do not 
correlate well to my fluorescence scores from sorting, so I am optimizing the
backbone for each of these mutant sequences after to see if it will more accurately
predict the dimerization strength of my mutant sequences.
"""

# read in energy file from command line 
energyAndFluorFile = sys.argv[1]
df_energyAndFluor = pd.read_csv(energyAndFluorFile)
# get just the mutants sequences
df_mutants = df_energyAndFluor[df_energyAndFluor['Sequence'].isin(df_energyAndFluor['StartSequence']) == False]
# get the output directory (currently same directory as energy file)
programPath = os.path.realpath(energyAndFluorFile)
programDir, programFile = os.path.split(programPath)
outputDir = programDir
#the below makes a csv file for running condor backboneOptimizer on all of the mutant sequences
optimizeFile = outputDir+'/allMutants.csv'
colsToAdd = ['Sequence','xShift','crossingAngle','axialRotation','zShift','DesignDir']
with open(optimizeFile, 'w') as f:
    # loop through all rows to get the desired information for the csv for each sequence 
    for index, row in df_mutants.iterrows():
        # initialize string to output
        line = ''
        # loop through all of the given columns hardcoded above
        for col in colsToAdd:
            # kinda gross; needed to replace part of the dir path since I changed it recently, so coded it below to do so
            if 'Design' in col:
                #replace index 19-index for design with /Design_Data/12_06_2021_CHIP_dataset/
                value = str(row[col])
                start = value[:40]
                #TODO: edit this so that it get's the proper end if the design_number is longer/shorter
                # get the index of the parts of the path that won't be replaced
                designNumberIndex = value.find("/design")
                endDirPathIndex = value.find('backbone')
                pdbBeforeMutantDirIndex = value.find('/',endDirPathIndex)
                configEnd = value[designNumberIndex:endDirPathIndex]
                # for some reason, need to add 1 to include the / that I previously found
                pdbMiddle = value[designNumberIndex:pdbBeforeMutantDirIndex+1]
                pdbEnd = value[pdbBeforeMutantDirIndex:]
                replaceDir = '/Design_Data/12_06_2021_CHIP1_Dataset'
                newDir = start+replaceDir
                pdb = newDir+pdbMiddle+'mutants'+pdbEnd
                config = newDir+configEnd+'repack.config'
                line = line+','+config+','+pdb
            # needed to find a way to account for command line use of negative angle and rotation, coded that below
            elif 'crossingAngle' in col:
                value = row[col]
                if row[col] < 0:
                    value = value*(-1)
                    value = str(value)
                    line = line+','+value
                    line = line+',true'
                else:
                    value = str(value)
                    line = line+','+value
                    line = line+',false'
            elif 'axialRotation' in col:
                value = row[col]
                if row[col] < 0:
                    value = value*(-1)
                    value = str(value)
                    line = line+','+value
                    line = line+',true'
                else:
                    value = str(value)
                    line = line+','+value
                    line = line+',false'
            else:
                value = str(row[col])
                if line == '':
                    line = value
                else:
                    line = line+','+value
        line = line + '\n'
        f.write(line)
f.close()

print('Generate csv file: ', optimizeFile)