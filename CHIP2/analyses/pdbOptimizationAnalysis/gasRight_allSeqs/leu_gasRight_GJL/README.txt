
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
sequenceanalysis = sequenceAnalysis_JC.py


toxgreenConversion
outputdir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/toxgreenConversion/GASright_analysis/percentGpA_GAS_GJL
requirementsfile = requirements.txt
inputdir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/toxgreenConversion/GASright_analysis/inputFiles
reconstructionfile = /home/loiseau@ad.wisc.edu/github/Sequence-Design/ngsReconstruction/CHIP2_rerun_allSeqs/reconstructedData/reconstructionAllData.csv
wtsequencecomputationfile = allGasRightDesignEnergyFile.csv
mutantsequencecomputationfile = gasRightMutants.csv
scriptdir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/toxgreenConversion/code
adjustfluorscript = adjustFluorByControlFlow_percentGpA_stdFix.py
controlflowfile = controlToxgreen_withSeqs.csv
filteringscript = filterWithComputation_percentGpA_stdFix.py
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
outputdir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/gasRight/leu_gasRight_GJL
rawdatadir = /home/loiseau@ad.wisc.edu/senesDrive/General/data/data02/gloiseau/JC_data/JC_design_data/leucine_ends/
datafile = gasRight_leu_GJL
toxgreenfile = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/toxgreenConversion/GASright_analysis/percentGpA_GAS_GJL/filtered/all.csv
strippedsequencefile = strippedSequenceFile
requirementsfile = /home/loiseau@ad.wisc.edu/github/Sequence-Design/2022-2023_gblock/calcEnergy/requirements.txt
clashscript = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/clashingAnalysis/code/keepBestClashing.py
clashinputdir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/toxgreenConversion/GASright_analysis/percentGpA_GAS_GJL/sequenceVsMutant/all
kdefile = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/inputFiles/2020_09_23_kdeData.csv
mutant_cutoff = 0.25, 0.25, 0.30, 0.30, 0.35, 0.35, 0.40, 0.40, 0
percent_cutoff = 0.5, .75, 0.5, .75, 0.5, .75, 0.5, .75, 0
number_of_mutants_cutoff = 1, 2


sequenceAnalysis_JC
codedir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/sequenceAnalysis/code
clashdir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/gasRight/leu_gasRight_GJL
outputdir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/sequenceAnalysis/gasRight/leu_gasRight_GJL
requirementsfile = /home/loiseau@ad.wisc.edu/github/Sequence-Design/2022-2023_gblock/calcEnergy/requirements.txt
sequencefile = wt/plotData.csv
mutantfile = mutant/lowestEnergySequences.csv
