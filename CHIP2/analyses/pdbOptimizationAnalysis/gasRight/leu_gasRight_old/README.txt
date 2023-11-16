
This contains outputs for the pdbOptimizationAnalysis code. It extracts the energetics from a C++ program that predicts
structures of mutant proteins based on a given dimeric pdb structure. The analysis for those energies, according to the 
below given options, is found within this directory.


main
codedir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/code
outputdir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/gasRight/leu_gasRight
rawdatadir = /home/loiseau@ad.wisc.edu/senesDrive/General/data/data02/gloiseau/JC_data/JC_design_data/leucine_ends/
datafile = gasRight_leu
toxgreenfile = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/inputFiles/JC_reconstruction_data.csv
requirementsfile = /home/loiseau@ad.wisc.edu/github/Sequence-Design/2022-2023_gblock/calcEnergy/requirements.txt
disruptionscript = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/clashingAnalysis/code/keepBestClashing.py
disruptioninputdir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/fluorescenceAnalysis/GASright_analysis/percentGpA_GAS/sequenceVsMutant/all
kdefile = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/inputFiles/2020_09_23_kdeData.csv
mutant_cutoff = 0.25, 0.25, 0.30, 0.30, 0.35, 0.35, 0.40, 0.40
percent_cutoff = 0.5, .75, 0.5, .75, 0.5, .75, 0.5, .75
number_of_mutants_cutoff = 2, 2, 2, 2, 2, 2, 2, 2

mutant_cutoff is the cutoff for the PercentGpa. 
percent_cutoff is the cutoff for the difference between WT and mutant that is accepted.
number_of_mutants_cutoff is the number of mutants that must pass either of the above cutoffs to accept the WT sequence.