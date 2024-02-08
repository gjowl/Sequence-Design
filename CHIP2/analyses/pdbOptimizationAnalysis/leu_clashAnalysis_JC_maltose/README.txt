
This contains outputs for the pdbOptimizationAnalysis code. It extracts the energetics from a C++ program that predicts
structures of mutant proteins based on a given dimeric pdb structure. The analysis for those energies, according to the 
below given options, is found within this directory. Directories named as follows:
    - clash: trim by the clashing mutant data
    - mutant_cutoff: fluorescence cutoff that the mutant must be less than to accept
    - percent_cutoff: another cutoff for mutants where the mutant fluorescence must be at least this much less than the WT to be accepted
    - number_of_mutants: the number of mutants necessary to be accepted for the WT design to be accepted


pdbOptimizationAnalysis
codedir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/code
outputdir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/leu_clashAnalysis_JC_maltose
rawdatadir = /home/loiseau@ad.wisc.edu/senesDrive/General/data/data02/gloiseau/2020-2024_Sequence_Design_Project/2022-2023_DesignData/2023-9-5_allSeqsLeuEnds_bbOptimized
datafile = gasRight_leu
toxgreenfile = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/inputFiles/JC_reconstruction_data.csv
strippedsequencefile = strippedSequenceFile
requirementsfile = /home/loiseau@ad.wisc.edu/github/Sequence-Design/2022-2023_gblock/calcEnergy/requirements.txt
clashscript = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/clashingAnalysis/code/keepBestClashing.py
clashinputdir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/toxgreenConversion/GASright_analysis/percentGpA_GAS/sequenceVsMutant/all
kdefile = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/inputFiles/2020_09_23_kdeData.csv
mutant_cutoff = 0, 0.25, 0.30, 0.35, 0.40
percent_cutoff = 0, 0.25, 0.5, .75
number_of_mutants_cutoff = 1, 2
maltosefile = /home/loiseau@ad.wisc.edu/github/Sequence-Design/ngsReconstruction/JC_maltose_2023-12/fwd/reconstructedData/maltoseTest/percentDifference.csv
maltosecol = LB-0H_M9-36H
