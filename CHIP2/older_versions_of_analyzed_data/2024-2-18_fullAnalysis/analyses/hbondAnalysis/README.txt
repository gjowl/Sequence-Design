
This contains outputs for the hbondAnalysis code. It analyzes pdb structures to determine the number of 
hydrogen bonds that are possible based on a given distance cutoff, and it outputs analyzed data.


runAllAnalysis
toxgreenconversion = toxgreenConversion.py
pdboptimizationanalysis = pdbOptimizationAnalysis.py
sequenceanalysis = sequenceAnalysis.py
figuremaking = figureMaking.py
hbondanalysis = hbondAnalysis.py


toxgreenConversion
outputdir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/gjl_test/toxgreenConversion/
requirementsfile = requirements.txt
inputdir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/toxgreenConversion/inputFiles
reconstructionfile = /home/loiseau@ad.wisc.edu/github/Sequence-Design/ngsReconstruction/CHIP2_rerun_with_maltose/reconstructedData/reconstructionAllData.csv
wtsequencecomputationfile = chipEnergyFile.csv
mutantsequencecomputationfile = allMutants.csv
scriptdir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/toxgreenConversion/code
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
codedir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/code
outputdir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/gjl_test/analyses/pdbOptimizationAnalysis/
rawdatadir = /home/loiseau@ad.wisc.edu/senesDrive/General/data/data02/gloiseau/2020-2024_Sequence_Design_Project/2022-2024_DesignData/2024-2-18_pdbBBOptimization_reruns/leu_wts/
datafile = leu_data
toxgreenfile = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/gjl_test/toxgreenConversion/filtered/all.csv
strippedsequencefile = strippedSequenceFile
requirementsfile = /home/loiseau@ad.wisc.edu/github/Sequence-Design/2022-2023_gblock/calcEnergy/requirements.txt
clashscript = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/clashingAnalysis/code/keepBestClashing.py
clashinputdir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/gjl_test/toxgreenConversion/sequenceVsMutant/all
kdefile = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/pdbOptimizationAnalysis/inputFiles/2020_09_23_kdeData.csv
mutant_cutoff = 0, 0.25, 0.30, 0.35, 0.40
percent_cutoff = 0, 0.25, 0.5, .75
number_of_mutants_cutoff = 1, 2
maltosefile = /home/loiseau@ad.wisc.edu/github/Sequence-Design/ngsReconstruction/CHIP2_rerun_with_maltose/reconstructedData/maltoseTest/percentDifference.csv
maltosecol = LB-0H_M9-30H


sequenceAnalysis
codedir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/sequenceAnalysis/code
clashdir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/gjl_test/analyses/pdbOptimizationAnalysis/
outputdir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/gjl_test/analyses/sequenceAnalysis/
requirementsfile = /home/loiseau@ad.wisc.edu/github/Sequence-Design/2022-2023_gblock/calcEnergy/requirements.txt
sequencefile = wt/plotData.csv
mutantfile = mutant/lowestEnergySequences.csv


figureMaking
codedir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/figureMaking/code/
rawdatadirleu = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/2023-3-7_leu/pdbs
rawdatadirala = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/2023-3-13_ala/pdbs
optimizedpdbdirleu = /home/loiseau@ad.wisc.edu/senesDrive/General/data/data02/gloiseau/2020-2024_Sequence_Design_Project/2022-2024_DesignData/2024-2-18_pdbBBOptimization_reruns/leu_wts/
optimizedpdbdirala = /home/loiseau@ad.wisc.edu/senesDrive/General/data/data02/gloiseau/2020-2024_Sequence_Design_Project/2022-2024_DesignData/2024-2-18_pdbBBOptimization_reruns/leu_wts/
outputdir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/gjl_test/analyses/figureMaking/
outputfile = wt_merge
percentgpacutoff = 0
sequencefile = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/gjl_test/analyses/pdbOptimizationAnalysis/clash_35_50_1/wt.csv
datafile = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/gjl_test/analyses/pdbOptimizationAnalysis/leu_data_percentGpa_maltose.csv
interfacefile = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/figureMaking/inputFiles/interfaceDataFile.csv
requirementsfile = /home/loiseau@ad.wisc.edu/github/Sequence-Design/2022-2023_gblock/calcEnergy/requirements.txt


hbondAnalysis
codedir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/hbondAnalysis/code
psedir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/gjl_test/analyses/figureMaking/interfacePdbs/pse/
outputdir = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/gjl_test/analyses/hbondAnalysis/
hbondfile = hbondFile
plotdatafile = plotDataFile
datafile = /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/gjl_test/analyses/figureMaking/wt_merge_leu.csv
requirementsfile = /home/loiseau@ad.wisc.edu/github/Sequence-Design/2022-2023_gblock/calcEnergy/requirements.txt
hbonddistance = 3
