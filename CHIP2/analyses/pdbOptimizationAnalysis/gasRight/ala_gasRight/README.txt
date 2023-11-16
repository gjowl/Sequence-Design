
This contains outputs for the pdbOptimizationAnalysis code. It extracts the energetics from a C++ program that predicts
structures of mutant proteins based on a given dimeric pdb structure. The analysis for those energies, according to the 
below given options, is found within this directory. Directories named as follows:
    - clash: trim by the clashing mutant data
    - mutant_cutoff: fluorescence cutoff that the mutant must be less than to accept
    - percent_cutoff: another cutoff for mutants where the mutant fluorescence must be at least this much less than the WT to be accepted
    - number_of_mutants: the number of mutants necessary to be accepted for the WT design to be accepted


main
codedir = /mnt/d/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/code
outputdir = /mnt/d/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/gasRight/ala_gasRight
rawdatadir = /mnt/d/gasRight_designs/JC_ala/
datafile = gasRight_ala
toxgreenfile = /mnt/d/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/inputFiles/JC_reconstruction_data.csv
requirementsfile = /mnt/d/github/Sequence-Design/2022-2023_gblock/calcEnergy/requirements.txt
disruptionscript = /mnt/d/github/Sequence-Design/CHIP2/analyses/clashingAnalysis/code/keepBestClashing.py
disruptioninputdir = /mnt/d/github/Sequence-Design/CHIP2/fluorescenceAnalysis/GASright_analysis/percentGpA_GAS/sequenceVsMutant/all
kdefile = /mnt/d/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/inputFiles/2020_09_23_kdeData.csv
mutant_cutoff = 0.25, 0.25, 0.30, 0.30, 0.35, 0.35, 0.40, 0.40
percent_cutoff = 0.5, .75, 0.5, .75, 0.5, .75, 0.5, .75
number_of_mutants_cutoff = 1
