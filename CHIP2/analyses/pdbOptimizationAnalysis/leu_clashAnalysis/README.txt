
This contains outputs for the pdbOptimizationAnalysis code. It extracts the energetics from a C++ program that predicts
structures of mutant proteins based on a given dimeric pdb structure. The analysis for those energies, according to the 
below given options, is found within this directory.


main
codedir = /mnt/d/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/code
outputdir = /mnt/d/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/leu_clashAnalysis
rawdatadir = /mnt/d/senesDrive/General/data/data02/gloiseau/2020-2024_Sequence_Design_Project/2022-2023_DesignData/2023-9-5_allSeqsLeuEnds_bbOptimized
datafile = leu_data
toxgreenfile = /mnt/d/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/inputFiles/stdFix_stripped_seqs.csv
requirementsfile = /mnt/d/github/Sequence-Design/2022-2023_gblock/calcEnergy/requirements.txt
disruptionscript = /mnt/d/github/Sequence-Design/CHIP2/analyses/clashingAnalysis/code/keepBestClashing.py
disruptioninputdir = /mnt/d/github/Sequence-Design/CHIP2/fluorescenceAnalysis/analysis_with_toxgreenSeqs_percentGpA_stdFix/sequenceVsMutant/all
kdefile = /mnt/d/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/inputFiles/2020_09_23_kdeData.csv
mutant_cutoff = 0.25, 0.25, 0.30, 0.30, 0.35, 0.35, 0.40, 0.40
percent_cutoff = 0.5, .75, 0.5, .75, 0.5, .75, 0.5, .75
number_of_mutants_cutoff = 2, 2, 2, 2, 2, 2, 2
