
This contains outputs for the pdbOptimizationAnalysis code. It extracts the energetics from a C++ program that predicts
structures of mutant proteins based on a given dimeric pdb structure. The analysis for those energies, according to the 
below given options, is found within this directory. Directories named as follows:
    - clash: trim by the clashing mutant data
    - mutant_cutoff: fluorescence cutoff that the mutant must be less than to accept
    - percent_cutoff: another cutoff for mutants where the mutant fluorescence must be at least this much less than the WT to be accepted
    - number_of_mutants: the number of mutants necessary to be accepted for the WT design to be accepted


runAllAnalysis
toxgreenconversion = toxgreenConversion.py
pdboptimizationanalysis = pdbOptimizationAnalysis.py
sequenceanalysis = sequenceAnalysis.py
structureanalysis = structureAnalysis.py
hbondanalysis = hbondAnalysis.py
outputdir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/JC_CHIP4
analysiscodedir = analyses
runtoxgreenconversion = true
runpdboptimizationanalysis = true
runsequenceanalysis = false
runstructureanalysis = false
runhbondanalysis = false
helperscript = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/helperCode.py


toxgreenConversion
requirementsfile = requirements.txt
inputdir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/toxgreenConversion/GASright_analysis/inputFiles
reconstructionfile = /home/loiseau@ad.wisc.edu/github/Sequence-Design/ngsReconstruction/JC_CHIP4/analyzedData/reconstructionAllData.csv
wtsequencecomputationfile = reconstructionAllData.csv
mutantsequencecomputationfile = All_GAS_to_I.csv
scriptdir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/toxgreenConversion/code
adjustfluorscript = adjustFluorByControlFlow_percentGpA_stdFix_fluor.py
controlflowfile = controlToxgreen_noMajorOutliers.csv
filteringscript = filterWithComputation_percentGpA_stdFix_CHIP4.py
filteringdir = filtered
graphingdir = graphed
sequencevsmutantscript = sequenceVsMutant.py
seqdir = sequenceVsMutant
graphscript = graphComputationVsExperiment.py
graphscript2 = graphDesignWts.py
runadjustfluor = true
runfilterwithcomputation = true
runsequencevsmutant = true
runfilterbeforegraphing = true
rungraphing = true


pdbOptimizationAnalysis
codedir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/code
inputdir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/JC_CHIP4/pdbOptimizationAnalysis/inputFiles
scriptdir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/code
rawdatadir = /home/loiseau@ad.wisc.edu/senesDrive/General/data/data02/gloiseau/JC_data/JC_design_data/pdbs_repacked_leucine_ends/JC_wt/
sequencefile = sequence_fluor_energy_data.csv
mutantfile = mutant_fluor_energy_data.csv
toxgreenfile = all.csv
requirementsfile = requirements.txt
clashscript = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/code/keepBestClashing.py
clashinputdir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/JC_CHIP4/toxgreenConversion/sequenceVsMutant/all
kdefile = 2020_09_23_kdeData.csv
mutant_cutoff = 0, 0.35
percent_cutoff = 0, 0.5
number_of_mutants_cutoff = 1
maltosefile = percentDifference.csv
maltoseseq = VVATSLVVLTLGVLLAFL
maltosecol = LB-0H_M9-30H


sequenceAnalysis
codedir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/sequenceAnalysis/code
clashdir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/JC_GAS/analyses/pdbOptimizationAnalysis/
requirementsfile = /home/loiseau@ad.wisc.edu/github/Sequence-Design/2022-2023_gblock/calcEnergy/requirements.txt
sequencefile = wt/plotData.csv
mutantfile = mutant/lowestEnergySequences.csv
