
This contains outputs for the sequenceAnalysis code. It takes the data from the reconstructed fluorescence of trimmed datasets
and analyzes the sequence composition against the fluorescence. Directories are named as follows:
    - clash: trim by the clashing mutant data
    - mutant_cutoff: fluorescence cutoff that the mutant must be less than to accept
    - percent_cutoff: another cutoff for mutants where the mutant fluorescence must be at least this much less than the WT to be accepted
    - number_of_mutants: the number of mutants necessary to be accepted for the WT design to be accepted


runAllAnalysis
toxgreenconversion = toxgreenConversion.py
pdboptimizationanalysis = pdbOptimizationAnalysis.py
sequenceanalysis = sequenceAnalysis.py
hbondanalysis = hbondAnalysis.py
structureanalysis = structureAnalysis.py
outputdir = /mnt/d/github/Sequence-Design/CHIP2/2024-7-7_updatedRepacks/
analysiscodedir = analyses
runtoxgreenconversion = false
runpdboptimizationanalysis = true
runsequenceanalysis = true
runstructureanalysis = false
runhbondanalysis = false
helperscript = /mnt/d/github/Sequence-Design/CHIP2/analyses/helperCode.py


toxgreenConversion
requirementsfile = requirements.txt
inputdir = /mnt/d/github/Sequence-Design/CHIP2/analyses/toxgreenConversion/inputFiles
reconstructionfile = /mnt/d/github/Sequence-Design/ngsReconstruction/CHIP2_rerun_with_maltose/reconstructedData/reconstructionAllData.csv
wtsequencecomputationfile = chipEnergyFile.csv
mutantsequencecomputationfile = allMutants.csv
scriptdir = /mnt/d/github/Sequence-Design/CHIP2/analyses/toxgreenConversion/code
adjustfluorscript = adjustFluorByControlFlow_percentGpA_stdFix_fluor.py
controlflowfile = 2023-11-4_controlToxgreen.csv
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
codedir = /mnt/d/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/code
inputdir = /mnt/d/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/inputFiles
scriptdir = /mnt/d/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/code
rawdatadir = /mnt/d/2024-6-12_CHIP2_optimized_data/CHIP2_all/
datafile = leu_data
mutantfile = /mnt/d/github/Sequence-Design/CHIP2/2024-7-7_updatedRepacks/toxgreenConversion/filtered/mutant_fluor_energy_data.csv
sequencefile = /mnt/d/github/Sequence-Design/CHIP2/2024-7-7_updatedRepacks/toxgreenConversion/filtered/sequence_fluor_energy_data.csv
toxgreenfile = /mnt/d/github/Sequence-Design/CHIP2/2024-7-7_updatedRepacks/toxgreenConversion/filtered/all.csv
strippedsequencefile = strippedSequenceFile
requirementsfile = /mnt/d/github/Sequence-Design/2022-2023_gblock/calcEnergy/requirements.txt
clashscript = /mnt/d/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/code/keepBestClashing_v2.py
kdefile = /mnt/d/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/inputFiles/2020_09_23_kdeData.csv
mutant_cutoff = 0, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6
percent_cutoff = 0
number_of_mutants_cutoff = 0
maltosefile = /mnt/d/github/Sequence-Design/ngsReconstruction/CHIP2_rerun_with_maltose/reconstructedData/maltoseTest/percentDifference.csv
maltosecol = LB-0H_M9-30H
maltoseseq = VVATSLVVLTLGVLLAFL


sequenceAnalysis
codedir = /mnt/d/github/Sequence-Design/CHIP2/analyses/sequenceAnalysis/code
clashdir = /mnt/d/github/Sequence-Design/CHIP2/2024-7-7_updatedRepacks/pdbOptimizationAnalysis/
requirementsfile = /mnt/d/github/Sequence-Design/2022-2023_gblock/calcEnergy/requirements.txt
sequencecsv = wt/dataForSeqAnalysis.csv
mutantcsv = mutant/dataForSeqAnalysis.csv
toxgreenfile = /mnt/d/github/Sequence-Design/CHIP2/2024-7-7_updatedRepacks/toxgreenConversion/filtered/all.csv
