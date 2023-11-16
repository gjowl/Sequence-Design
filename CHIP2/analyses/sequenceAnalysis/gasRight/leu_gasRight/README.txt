
This contains outputs for the sequenceAnalysis code. It takes the data from the reconstructed fluorescence of trimmed datasets
and analyzes the sequence composition against the fluorescence. Directories are named as follows:
    - clash: trim by the clashing mutant data
    - mutant_cutoff: fluorescence cutoff that the mutant must be less than to accept
    - percent_cutoff: another cutoff for mutants where the mutant fluorescence must be at least this much less than the WT to be accepted
    - number_of_mutants: the number of mutants necessary to be accepted for the WT design to be accepted


main
codedir = /mnt/d/github/Sequence-Design/CHIP2/analyses/sequenceAnalysis/code
clashdir = /mnt/d/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/gasRight/leu_gasRight
outputdir = /mnt/d/github/Sequence-Design/CHIP2/analyses/sequenceAnalysis/gasRight/leu_gasRight
requirementsfile = /mnt/d/github/Sequence-Design/2022-2023_gblock/calcEnergy/requirements.txt
sequencefile = wt/lowestEnergySequences.csv
mutantfile = mutant/lowestEnergySequences.csv
