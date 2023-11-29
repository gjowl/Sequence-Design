
This contains outputs for the pdbOptimizationAnalysis code. It extracts the energetics from a C++ program that predicts
structures of mutant proteins based on a given dimeric pdb structure. The analysis for those energies, according to the 
below given options, is found within this directory. Directories named as follows:
    - clash: trim by the clashing mutant data
    - mutant_cutoff: fluorescence cutoff that the mutant must be less than to accept
    - percent_cutoff: another cutoff for mutants where the mutant fluorescence must be at least this much less than the WT to be accepted
    - number_of_mutants: the number of mutants necessary to be accepted for the WT design to be accepted


main
codedir = /mnt/d/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/code
outputdir = /mnt/d/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/leu_clashAnalysis_rerun
rawdatadir = /mnt/d/senesDrive/General/data/data02/gloiseau/2020-2024_Sequence_Design_Project/2022-2023_DesignData/2023-9-5_allSeqsLeuEnds_bbOptimized
datafile = leu_data
toxgreenfile = /mnt/d/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/inputFiles/stripped_seqs_CHIP2_rerun.csv
requirementsfile = /mnt/d/github/Sequence-Design/2022-2023_gblock/calcEnergy/requirements.txt
clashscript = /mnt/d/github/Sequence-Design/CHIP2/analyses/clashingAnalysis/code/keepBestClashing.py
clashinputdir = /mnt/d/github/Sequence-Design/CHIP2/toxgreenConversion/CHIP2_rerun/sequenceVsMutant/all
kdefile = /mnt/d/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/inputFiles/2020_09_23_kdeData.csv
mutant_cutoff = 0, 0.25, 0.30, 0.35, 0.40
percent_cutoff = 0, 0.25, 0.5, .75
number_of_mutants_cutoff = 1, 2
