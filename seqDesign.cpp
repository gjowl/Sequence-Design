/**
 * @Author: Gilbert Loiseau
 * @Date:   2022/02/11
 * @Email:  gjowl04@gmail.com
 * @Filename: seqDesign.cpp
 * @Last modified by:   Gilbert Loiseau
 * @Last modified time: 2022/02/15
 */
#include <sstream>
#include <iterator>
#include <unistd.h>

// MSL Functions
#include "System.h"
#include "CharmmSystemBuilder.h"
#include "SystemRotamerLoader.h"
#include "OptionParser.h"
#include "SelfPairManager.h"
#include "MslTools.h"
#include "DeadEndElimination.h"
#include "SelfConsistentMeanField.h"
#include "HydrogenBondBuilder.h"
#include "Transforms.h"
#include "RandomNumberGenerator.h"
#include "MonteCarloManager.h"
#include "AtomSelection.h"
#include "AtomContainer.h"
#include "FormatConverter.h"
#include "CRDReader.h"
#include "CRDWriter.h"
#include "SysEnv.h"
#include "ResidueSelection.h"
#include "BaselineEnergyBuilder.h"
#include "BaselineInteraction.h"

// Design Functions: TODO figure out which of these are necessary; a lot of this code I just added internally I believe
#include "BaselineIMM1Interaction.h"
#include "BaselinePairInteraction.h"
#include "BaselineOuterPairInteraction.h"
#include "BaselineAAComposition.h"
#include "BaselineSequenceEntropy.h"
#include "BaselineSequenceEntropyNormalized.h"
#include "BaselinePermutation.h"
#include "SasaCalculator.h"
#include "designFunctions.h"
#include "design_options.h"

using namespace MSL;
using namespace std;

static SysEnv SYSENV;
string programName = "seqDesign";//TODO: better name
string programDescription = "Designs sequences for backbone geometries extracted from the PDB, optimizing specifically for vdW energies";
string programAuthor = "Gilbert Loiseau";
string programVersion = "2";
string programDate = "11 February 2022";
string mslVersion = MSLVERSION;
string mslDate = MSLDATE;

time_t startTime, endTime, spmStart, spmEnd;
double diffTime, spmTime;

/**************************************************
 *
 *  =======  INTERNAL FUNCTIONS  =======
 *
 **************************************************/
// parse config file for given options
Options parseOptions(int _argc, char * _argv[], Options defaults);

//Keep functions that need each other to work together
/***********************************
 *help functions
 ***********************************/
void usage();
void help(Options defaults);
void outputErrorMessage(Options &_opt);

/******************************************
 *
 *  =======  BEGIN MAIN =======
 *
 ******************************************/
int main(int argc, char *argv[]){

	time_t rawtime;
	struct tm * timeinfo;
	char buffer[80];

	time(&startTime);
	time (&rawtime);
	timeinfo = localtime(&rawtime);

	strftime(buffer,sizeof(buffer),"%m_%d_%Y",timeinfo);
	string date(buffer);

	/******************************************************************************
	 *                 === PARSE THE COMMAND LINE OPTIONS ===
	 ******************************************************************************/
	Options defaults;
	//Add in some default options that can easily be changed here
	Options opt = parseOptions(argc, argv, defaults);

	if (opt.errorFlag) {
		outputErrorMessage(opt);
		exit(1);
	}

	/******************************************************************************
	 *                       === SETUP OUTPUT FILES ===
	 ******************************************************************************/
	// summary file output
	ofstream sout;
	// error file output
	ofstream err;
	// rerun config output
	ofstream rerun;

	setupDesignDirectory(opt, date);

	string soutfile = opt.pdbOutputDir + "/summary.out";
	string errfile  = opt.pdbOutputDir + "/errors.out";
	string rerunfile = opt.pdbOutputDir + "/rerun.config";

	sout.open(soutfile.c_str());
	err.open(errfile.c_str());
	rerun.open(rerunfile.c_str());

	rerun << opt.rerunConf << endl;
	rerun.close();

	sout << date << endl;
	err << date << endl;

	/******************************************************************************
	 *               === LOAD RANDOM GEOMETRY FROM GEOMETRY FILE ===
	 ******************************************************************************/
	// Initialize RNG with seed (time or given seed number)
	RandomNumberGenerator RNG;
	if (opt.useTimeBasedSeed){
		RNG.setTimeBasedSeed();
	} else {
		RNG.setSeed(opt.seed);
	}

	// TODO:...
	vector<double> densities;
	if (opt.getGeoFromPDBData){
		getGeometry(opt, RNG, densities, sout);
	}

	// Output the starting geometry
	cout << "***STARTING GEOMETRY:***" << endl;
	cout << "xShift:        " << opt.xShift << "\tDensity: " << densities[0] << endl;
	cout << "crossingAngle: " << opt.crossingAngle << "\tDensity: " << densities[0] << endl;
	cout << "axialRotation: " << opt.axialRotation << "\tDensity: " << densities[1] << endl;
	cout << "zShift:        " << opt.zShift << "\tDensity: " << densities[2] << endl << endl;

	//String for the alternateIds at the interface
	string alternateIds = getAlternateIdString(opt.Ids);
	cout << "Amino acids for design: LEU " << alternateIds << endl;

	/******************************************************************************
	 *                       === GENERATE POLYMER SEQUENCE ===
	 ******************************************************************************/
	string polySeq = generatePolymerSequence(opt.backboneAA, opt.backboneLength, opt.thread);
	PolymerSequence PS(polySeq);

	/******************************************************************************
	 *                     === HELICAL AXIS SET UP ===
	 ******************************************************************************/
	string axis = "\
ATOM      1  O   DUM A   1       0.000   0.000   0.000  1.00  0.00           P\n\
ATOM      2  Z   DUM A   1       0.000   0.000   1.000  1.00  0.00           O\n\
TER\n\
ATOM      3  O   DUM B   1       0.000   0.000   0.000  1.00  0.00           P\n\
ATOM      4  Z   DUM B   1       0.000   0.000   1.000  1.00  0.00           O\n\
TER\n\
END";

	PDBReader readAxis;
	if(!readAxis.read(axis)) {
		err << "Unable to read axis" << endl;
		exit(0);
	}

	System helicalAxis;
	helicalAxis.addAtoms(readAxis.getAtomPointers());

	AtomPointerVector &axisA = helicalAxis.getChain("A").getAtomPointers();
	AtomPointerVector &axisB = helicalAxis.getChain("B").getAtomPointers();

	// Reference points for Helices
	CartesianPoint ori(0.0,0.0,0.0);
	CartesianPoint zAxis(0.0,0.0,1.0);
	CartesianPoint xAxis(1.0,0.0,0.0);

	/******************************************************************************
	 *       === IDENTIFY INTERFACIAL POSITIONS AND GET ROTAMER ASSIGNMENTS ===
	 ******************************************************************************/
	// Variables to output from defineInterfaceAndRotamerSampling function
	string rotamerLevels;
	string variablePositionString;
	string rotamerSamplingString;
	// vector of the positions that will be linked
	vector<int> linkedPositions;
	// vector of positions at the interface excluding termini positions
	vector<uint> interfacePositions;
	// vector of positions at the interface including the terminal positions
	vector<uint> allInterfacePositions;
	// vector of rotamer level for each position
	vector<int> rotamerSamplingPerPosition;

	// Defines the interfacial positions and the number of rotamers to give each position
	defineInterfaceAndRotamerSampling(opt, PS, rotamerLevels, polySeq, variablePositionString, rotamerSamplingString, linkedPositions, allInterfacePositions, interfacePositions, rotamerSamplingPerPosition, sout, axis);

	/******************************************************************************
	 *         === COPY BACKBONE COORDINATES AND TRANSFORM TO GEOMETRY ===
	 ******************************************************************************/
	// initialize the gly69 backbone coordinates and transform it to the chosen geometry
	System pdb;
	pdb.readPdb(opt.infile);

	// Set up chain A and chain B atom pointer vectors
	Chain & chainA = pdb.getChain("A");
	Chain & chainB = pdb.getChain("B");
	AtomPointerVector & apvChainA = chainA.getAtomPointers();
	AtomPointerVector & apvChainB = chainB.getAtomPointers();

	// Set up object used for transformations
	Transforms trans;
	trans.setTransformAllCoors(true); // transform all coordinates (non-active rotamers)
	trans.setNaturalMovements(true); // all atoms are rotated such as the total movement of the atoms is minimized

	// Transform to chosen geometry
	transformation(apvChainA, apvChainB, axisA, axisB, ori, xAxis, zAxis, opt.zShift, opt.axialRotation, opt.crossingAngle, opt.xShift, trans);
	moveZCenterOfCAMassToOrigin(pdb.getAtomPointers(), helicalAxis.getAtomPointers(), trans);

	/******************************************************************************
	 *  === DECLARE SYSTEM FOR POLYLEU WITH ALTERNATE IDENTITIES AT INTERFACE ===
	 ******************************************************************************/
	// Initialize system for dimer to design
	System sys;
	// Initialize CharmmSystemBuilder to build energy terms for design
	CharmmSystemBuilder CSB(sys, opt.topFile, opt.parFile, opt.solvFile);
	// Explicit definitions of which terms to use and which to not use
	CSB.setBuildTerm("CHARMM_ELEC", false);
	CSB.setBuildTerm("CHARMM_ANGL", false);
	CSB.setBuildTerm("CHARMM_BOND", false);
	CSB.setBuildTerm("CHARMM_DIHE", false);
	CSB.setBuildTerm("CHARMM_IMPR", false);
	CSB.setBuildTerm("CHARMM_U-BR", false);
	CSB.setBuildTerm("CHARMM_IMM1REF", true);
	CSB.setBuildTerm("CHARMM_IMM1", true);

	CSB.setSolvent("MEMBRANE");
	CSB.setIMM1Params(15, 10);

	CSB.setBuildNonBondedInteractions(false);

	// Setup polymer sequence and build the sequence using CharmmSystemBuilder
	PolymerSequence PL(polySeq);
	if(!CSB.buildSystem(PL)) {
		err << "Unable to build system from " << polySeq << endl;
		exit(0);
	}

	/******************************************************************************
	 *                     === COPY BACKBONE COORDINATES ===
	 ******************************************************************************/
	// assign the coordinates of our system to the given geometry that was assigned without energies using System pdb
	sys.assignCoordinates(pdb.getAtomPointers(),false);
	sys.buildAllAtoms();

	// initialize the object for loading rotamers into our system
	SystemRotamerLoader sysRot(sys, opt.rotLibFile);
	sysRot.defineRotamerSamplingLevels();

	// Add hydrogen bond term
	HydrogenBondBuilder hb(sys, opt.hbondFile);
	hb.buildInteractions(50);//when this is here, the HB weight is correct

	/******************************************************************************
	 *                     === INITIAL VARIABLE SET UP ===
	 ******************************************************************************/
	// Initialize EnergySet that contains energies for the chosen terms for our design
	EnergySet* Eset = sys.getEnergySet();
	// Set all terms active, besides Charmm-Elec
	Eset->setAllTermsInactive();
	Eset->setTermActive("CHARMM_ELEC", false);
	Eset->setTermActive("CHARMM_ANGL", false);
	Eset->setTermActive("CHARMM_BOND", false);
	Eset->setTermActive("CHARMM_DIHE", false);
	Eset->setTermActive("CHARMM_IMPR", false);
	Eset->setTermActive("CHARMM_U-BR", false);
	Eset->setTermActive("CHARMM_VDW", true);
	Eset->setTermActive("SCWRL4_HBOND", true);
	Eset->setTermActive("CHARMM_IMM1REF", true);
	Eset->setTermActive("CHARMM_IMM1", true);

	// Set weights
	Eset->setWeight("CHARMM_VDW", opt.weight_vdw);
	Eset->setWeight("SCWRL4_HBOND", opt.weight_hbond);
	Eset->setWeight("CHARMM_IMM1REF", opt.weight_solv);
	Eset->setWeight("CHARMM_IMM1", opt.weight_solv);

	/******************************************************************************
	 *                === DELETE TERMINAL HYDROGEN BOND INTERACTIONS ===
	 ******************************************************************************/
	// removes all hydrogen bonding near the termini of our helices (remnant from CATM, but used in the code that was used to get baselines so keeping it to be consistent)
	deleteTerminalHydrogenBondInteractions(sys,opt);

	/******************************************************************************
	 *                === CHECK TO SEE IF ALL ATOMS ARE BUILT ===
	 ******************************************************************************/
	// check to verify that all atoms have coordinates
	checkIfAtomsAreBuilt(sys, err);

	/******************************************************************************
	 *                     === ADD IN BASELINE ENERGIES ===
	 ******************************************************************************/
	//
	if (opt.useBaseline){
		//addBaselineToSelfPairManager();//TODO: was going to make this a function but I feel like it already exists in spm, so going to wait when I have time to look that up
		//initialize baseline maps to calculate energy for each sequence for comparison in baselineMonomerComparison_x.out
		map<string, double> selfMap = readSingleParameters(opt.selfEnergyFile);
		map<string,map<string,map<uint,double>>> pairMap = readPairParameters(opt.pairEnergyFile);
		buildSelfInteractions(sys, selfMap);
		buildPairInteractions(sys, pairMap);
	}

	// TODO: change this; I feel like this should be an option if linked is true
	vector<vector<string>> linkedPos = convertToLinkedFormat(sys, linkedPositions, opt.backboneLength);
	sys.setLinkedPositions(linkedPos);

	// Get sequence entropy map
	map<string, double> sequenceEntropyMap = readSingleParameters(opt.sequenceEntropyFile);

	//decided to try loading low number of rotamers for this instead of high
	loadRotamers(sys, sysRot, opt, rotamerSamplingPerPosition);
	CSB.updateNonBonded(10,12,50);//This for some reason updates the energy terms and makes the IMM1 terms active (still need to check where, but did a couple of calcEnergy and outputs
	sys.calcEnergy();

	/******************************************************************************
	 *                        === SETUP SPM AND RUN SCMF ===
	 ******************************************************************************/
	//TODO: make it so that this part is optional: if I submit a sequence to start, don't even do this. Just find the interface, greedy for best sequence, and continue
	SelfPairManager spm;
	spm.seed(RNG.getSeed());
	spm.setSystem(&sys);
	spm.setVerbose(false);
	spm.setRunDEE(opt.runDEESingles, opt.runDEEPairs);
	spm.setOnTheFly(false);
	spm.setMCOptions(1000, 0.5, 5000, 3, 10, 1000, 0.01);//changed to sigmoid and added up to 5000
	spm.saveEnergiesByTerm(true); //added back in on 09_21_2021 to get the vdw and hbond energies
	spm.calculateEnergies();

	//Setup running SCMF or UnbiasedMC
	if (opt.runSCMF == true){
		cout << "Running Self Consistent Mean Field" << endl;
		sout << "Running Self Consistent Mean Field" << endl;
		spm.setRunSCMF(true);
		spm.setRunSCMFBiasedMC(true);
		spm.setRunUnbiasedMC(false);
	} else {
		cout << "runSCMF is false; Run Unbiased Monte Carlo " << endl;
		sout << "runSCMF is false; Run Unbiased Monte Carlo " << endl;
		spm.setRunSCMF(false);
		spm.setRunSCMFBiasedMC(false);
		spm.setRunUnbiasedMC(true);
	}

	// run and find a sequence using the chosen parameters (MCOptions, SCMF, DEE, etc.)
	time(&spmStart);
	spm.runOptimizer();
	time(&spmEnd);
	spmTime = difftime (spmEnd, spmStart);

	// vector for the initial SCMF state
	vector<unsigned int> initialState = spm.getSCMFstate();
	// vector for the SCMF state after the biased monte carlo
	vector<unsigned int> bestState = spm.getBestSCMFBiasedMCState();
	// define startingState vector as the bestState from the SelfPairManager optimizer
	vector<unsigned int> startingState = bestState;

	// energy terms from the startingState
	double bestEnergy = spm.getStateEnergy(bestState);
	double hbondEnergy = spm.getStateEnergy(bestState, "SCWRL4_HBOND");
	double vdwEnergy = spm.getStateEnergy(bestState, "CHARMM_VDW");

	// checks to see if the sequence changed between the initialState and the bestState
	sys.setActiveRotamers(initialState);
	string initialSeq = convertPolymerSeqToOneLetterSeq(sys.getChain("A"));
	sys.setActiveRotamers(bestState);
	string SCMFBestSeq = convertPolymerSeqToOneLetterSeq(sys.getChain("A"));
	sys.calcEnergy();
	string startSequence = SCMFBestSeq;//used for outputting starting sequence

	// TODO: make into a function?
	// output this information about the SelfPairManager run below
	string seqInterface = getInterfaceSequence(opt, rotamerSamplingString, startSequence);
	int numInterfacialPositions = linkedPos.size();
	cout << "Initial Sequence:   " << initialSeq << endl;
	cout << "Best Sequence:      " << startSequence << endl;
	cout << "Interface Sequence: " << seqInterface << endl;
	cout << "Interface:          " << variablePositionString << endl;
	cout << "Total Energy:       " << bestEnergy << endl;
	cout << "VDW:                " << vdwEnergy << endl;
	cout << "HBOND:              " << hbondEnergy << endl;
	sout << "Initial Sequence:   " << initialSeq << endl;
	sout << "Best Sequence:      " << startSequence << endl;
	sout << "Interface Sequence: " << seqInterface << endl;
	sout << "Interface:          " << variablePositionString << endl;
	sout << "Total Energy:       " << bestEnergy << endl;
	sout << "VDW:                " << vdwEnergy << endl;
	sout << "HBOND:              " << hbondEnergy << endl;
	sout << endl << "End SelfPairManager Optimization: " << spmTime << "s" << endl;
	cout << endl << "End SelfPairManager Optimization: " << spmTime << "s" << endl;

	/******************************************************************************
	 *           === METHODS FOR DETERMINING ALTERNATE SEQUENCES ===
	 ******************************************************************************/
	// Initialize vector to hold designed sequences
	vector<string> seqs;

	// Initialize vector to hold all designed sequences from the stateMC
	vector<string> allSeqs;

	//Initialize energyMap to hold all energies for output into a summary file
	map<string, map<string,double>> sequenceEnergyMap;

	// Initialize sequence and state pair vector: each sequence will be tied to it's state with the proper rotamers
	vector<pair<string,vector<uint>>> sequenceStatePair;

	/******************************************************************************
	 *      === MONTE CARLO TO RANDOMIZE SEQUENCES FROM BEST SCMF STATE ===
	 ******************************************************************************/
	// Unlink the best state from SCMF if not using linked positions during the state Monte Carlo
	if (!opt.linkInterfacialPositions){
		unlinkBestState(opt, bestState, rotamerSamplingPerPosition, opt.backboneLength);
		stateMCUnlinked(sys, opt, PL, sequenceEnergyMap, sequenceEntropyMap, bestState, seqs, allSeqs, sequenceStatePair, allInterfacePositions, interfacePositions, rotamerSamplingPerPosition, linkedPos, RNG, sout, err);
	} else {
		stateMCLinked(sys, spm, opt, PL, sequenceEnergyMap, sequenceEntropyMap, bestState, seqs, allSeqs, sequenceStatePair, interfacePositions, rotamerSamplingPerPosition, linkedPos, RNG, sout, err);
	}

	// I moved this on 12_6_2021: I noticed that I am getting too many threonines in my starting seqeunces, so I decided to move the baseline down here (this likely won't work for stateMCLinked, so I'll have to deal with that

	//Add energies for initial sequences into the sequenceEnergyMap
	seqs.insert(seqs.begin(), startSequence);
	pair<string,vector<uint>> startSequenceStatePair = make_pair(startSequence, startingState);
	sequenceStatePair.insert(sequenceStatePair.begin(), startSequenceStatePair);
	getEnergiesForStartingSequence(opt, spm, startSequence, startingState, sequenceEnergyMap, sequenceEntropyMap);
	getSasaForStartingSequence(sys, startSequence, startingState, sequenceEnergyMap);

	/******************************************************************************
	 *            === CALCULATE MONOMER ENERGIES OF EACH SEQUENCE ===
	 ******************************************************************************/
	computeMonomerEnergies(opt, trans, sequenceEnergyMap, seqs, RNG, sout, err);
	getSasaDifference(sequenceStatePair, sequenceEnergyMap);

	/******************************************************************************
	 *              === CALCULATE TOTAL ENERGIES AND WRITE PDBS ===
	 ******************************************************************************/
	// Initialize PDBWriter for designs
	PDBWriter writer;
	writer.open(opt.pdbOutputDir + "/allDesigns.pdb");

	// Output these energy calculations to the summary file
	sout << "Calculating Final Energies..." << endl;
	for (uint i=0; i<sequenceStatePair.size(); i++){
		string sequence = sequenceStatePair[i].first;
		vector<uint> state = sequenceStatePair[i].second;
		sout << "Sequence " << i+1 << ": " << sequence << endl;
		int seqNumber = i;
		// calculates the total energy difference between monomer and dimer and outputs individual pdbs for each sequence
		getTotalEnergyAndWritePdbs(sys, opt, sequenceEnergyMap, sequence, state, rotamerSamplingPerPosition, RNG, seqNumber, writer, sout, err);
	}
	writer.close();

	/******************************************************************************
	 *                   === WRITE OUT ENERGY AND DESIGN FILES ===
	 ******************************************************************************/
	outputDesignFiles(opt, rotamerSamplingString, rotamerSamplingPerPosition, sequenceStatePair, sequenceEnergyMap, densities);

	time(&endTime);
	diffTime = difftime (endTime, startTime);
	sout << "Total Time: " << setiosflags(ios::fixed) << setprecision(0) << diffTime/60 << " minutes" << endl;
	cout << "Total Time: " << setiosflags(ios::fixed) << setprecision(0) << diffTime/60 << " minutes" << endl;

	err.close();
	sout.close();
}

/*********************************
 *
 *  ======= FUNCTIONS =======
 *
 *********************************/

/***********************************
 *help functions
 ***********************************/
void usage() {
	cout << endl;
	cout << "Run as" << endl;
	//TODO: make this work tomorrow; should be able to organize this usage function and all of the stuff at the top properly; unless I move usage and other things to another file?
	//cout << "   % " << programName << " --configfile <file.config>" << endl;
	//cout << "For help" << endl;
	//cout << "   % " << programName << " -h" << endl;
	cout << endl;//TODO: add in some help options
}

void outputErrorMessage(Options &_opt){
		cerr << endl;
		cerr << "The program terminated with errors:" << endl;
		cerr << endl;
		cerr << _opt.errorMessages << endl;
		cerr << endl;
		cerr << _opt.OPerrors << endl;
		usage();
}

void help(Options defaults) {
	cout << "This program runs as:" << endl;
	cout << " % seqDesign " << endl;
	cout << "   Optional Parameters " << endl;
	cout << "   --topFile <file> --parFile <file> --solvFile <file> --hBondFile <file> --rotLibFile <file>" << endl;
	cout << "   --numberOfStructuresToMCRepack <int> --energyCutOff <double> --MCCycles <int> --MCMaxRejects=<int>" << endl;
	cout << "   --MCStartTemp <double> --MCEndTemp <double> --MCCurve <CONSTANT-0, LINEAR-1, EXPONENTIAL-2, SIGMOIDAL-3, SOFT-4>" << endl;
	cout << "   --greedyOptimizer=<true/false> --greedyCycles=<int>  --seed <int> --verbose <true/false>" << endl;
	cout << "   --thread <int>" << endl;
	cout << "   --configfile <file> " << endl;
	cout << "   --weight_hbond <double> --weight_vdw <double> --weight_solv <double> --weight_seqEntropy <double>" << endl;
	cout << "   --sasaRepackLevel <rotLevel> (in format SL95.00; 4 levels used by default) --interfaceLevel <int> " << endl << endl;
	cout << "Template Configuration file (copy and paste the below into a file.config and run code as bin/seqDesign --config file.config" << endl;
	cout << setw(20) << "backboneCrd " << defaults.backboneCrd << endl;
	cout << setw(20) << "pdbOutputDir " << defaults.pdbOutputDir << endl;

	cout << setw(20) << "tmStart " << defaults.tmStart << endl;
	cout << setw(20) << "tmEnd " << defaults.tmEnd << endl;

	cout << "#Input Files" << endl;
	cout << setw(20) << "topFile " << defaults.topFile << endl;
	cout << setw(20) << "parFile " << defaults.parFile << endl;
	cout << setw(20) << "geometryDensityFile " << defaults.geometryDensityFile << endl;
	cout << setw(20) << "rotLibFile " << defaults.rotLibFile << endl;
	cout << setw(20) << "solvFile " << defaults.solvFile << endl;
	cout << setw(20) << "backboneCrd " << defaults.backboneCrd << endl;
	cout << setw(20) << "hbondFile " << defaults.hbondFile << endl;
	cout << setw(20) << "infile " << defaults.infile << endl;
	cout << setw(20) << "selfEnergyFile " << defaults.selfEnergyFile << endl;
	cout << setw(20) << "pairEnergyFile " << defaults.pairEnergyFile << endl;
	cout << setw(20) << "AACompositionPenaltyFile " << defaults.AACompositionPenaltyFile << endl << endl;

	cout << "#Geometry and Transformation parameters" << endl;
	cout << setw(20) << "xShift" << defaults.xShift << endl;
	cout << setw(20) << "crossingAngle" << defaults.crossingAngle << endl;
	cout << setw(20) << "axialRotation" << defaults.axialRotation << endl;
	cout << setw(20) << "zShift" << defaults.zShift << endl;
	cout << setw(20) << "thread" << defaults.thread << endl;
	cout << setw(20) << "backboneLength " << defaults.backboneLength << endl;

	cout << "#Booleans" << endl;
	cout << setw(20) << "verbose " << defaults.verbose << endl;
	cout << setw(20) << "deleteTerminalHbonds" << defaults.deleteTerminalHbonds << endl;
	cout << setw(20) << "useSasa" << defaults.useSasa << endl;
	cout << setw(20) << "getGeoFromPDBData" << false << endl;//Since we already have the geometry output here, default to false in the rerun config
	cout << setw(20) << "runDEESingles" << defaults.runDEESingles << endl;
	cout << setw(20) << "runDEEPairs" << defaults.runDEEPairs << endl;
	cout << setw(20) << "runSCMF" << defaults.runSCMF << endl;
	//TODO: set this up so that instead of running through that, I just have the output sequence and state below
	if (defaults.runDEESingles == false && defaults.runDEEPairs == false && defaults.runSCMF == false){

	}

	if (defaults.useSasa == true){
		//cout << "#Load Rotamers based on SASA scores" << endl;
		for (uint i=0; i<defaults.sasaRepackLevel.size()-1; i++){
			cout << setw(20) << "sasaRepackLevel" << defaults.sasaRepackLevel[i] << endl;
		}
		cout << setw(20) << "interfaceLevel" << defaults.interfaceLevel << endl;
	} else {
		//cout << "#Load Rotamers by interface and non interfacial positions" << endl;
		cout << setw(20) << "SL" << defaults.SL << endl;
		cout << setw(20) << "SLInterface" << defaults.SLInterface << endl;
	}

	cout << "#MonteCarlo Paramenters" << endl;
	cout << setw(20) << "MCCycles" << defaults.MCCycles << endl;
	cout << setw(20) << "MCMaxRejects" << defaults.MCMaxRejects << endl;
	cout << setw(20) << "MCStartTemp" << defaults.MCStartTemp << endl;
	cout << setw(20) << "MCEndTemp" << defaults.MCEndTemp << endl;
	cout << setw(20) << "MCCurve" << defaults.MCCurve << endl;
	cout << setw(20) << "greedyCycles" << defaults.greedyCycles << endl;

	cout << "#Alternate IDs" << endl;
	for (uint i=0; i<defaults.Ids.size()-1; i++){
		cout << setw(20) << defaults.Ids[i] << endl;
	}

	cout << endl << "#Rerun Seed" << endl;
	cout << setw(20) << "seed" << defaults.seed << endl;

	cout << endl << "#Energy term weights" << endl;
	cout << setw(20) << "weight_vdw " << defaults.weight_vdw << endl;
	cout << setw(20) << "weight_hbond " << defaults.weight_hbond << endl;
	cout << setw(20) << "weight_solv " << defaults.weight_solv << endl;
	cout << setw(20) << "weight_seqEntropy " << defaults.weight_seqEntropy << endl;
	cout << endl;
}


/****************************************
 *
 *  ======= CONFIG FILE OPTIONS =======
 *
 ****************************************/
Options parseOptions(int _argc, char * _argv[], Options defaults){

	/******************************************
	 *  Pass the array of argument and the name of
	 *  a configuration file to the ArgumentParser
	 *  object.  Then ask for the value of the argument
	 *  and collect error and warnings.
	 *
	 *  This function returns a Options structure
	 *  defined at the head of this file
	 ******************************************/

	Options opt;

	/******************************************
	 *  Set the allowed and required options:
	 *
	 *  Example of configuration file:
	 *
	 *  /exports/home/gloiseau/mslib/trunk_AS/config/seqDesign.config
	 *
	 ******************************************/

	vector<string> required;
	vector<string> allowed;

	//opt.required.push_back("");
	//opt.allowed.push_back("");

	//opt.allowed.push_back("");
	// optional
	opt.allowed.push_back("getGeoFromPDBData");

	opt.allowed.push_back("sequence");
	opt.allowed.push_back("backboneAA");
	opt.allowed.push_back("backboneLength");

	opt.allowed.push_back("startResNum");
	opt.allowed.push_back("endResNum");
	opt.allowed.push_back("tmStart");
	opt.allowed.push_back("tmEnd");

	//Geometry
	opt.allowed.push_back("xShift");
	opt.allowed.push_back("crossingAngle");
	opt.allowed.push_back("axialRotation");
	opt.allowed.push_back("zShift");
	opt.allowed.push_back("transform");

	//Monte Carlo variables
	opt.allowed.push_back("MCCycles");
	opt.allowed.push_back("MCMaxRejects");
	opt.allowed.push_back("MCStartTemp");
	opt.allowed.push_back("MCEndTemp");
	opt.allowed.push_back("MCCurve");

	//Weights
	opt.allowed.push_back("weight_vdw");
	opt.allowed.push_back("weight_hbond");
	opt.allowed.push_back("weight_solv");
	opt.allowed.push_back("weight_seqEntropy");

	//Rotamers
	opt.allowed.push_back("SL");
	opt.allowed.push_back("SLInterface");

	//
	opt.allowed.push_back("verbose");
	opt.allowed.push_back("greedyOptimizer");
	opt.allowed.push_back("greedyCycles");
	opt.allowed.push_back("seed");

	// Cutoffs
	opt.allowed.push_back("printAllCrds");
	opt.allowed.push_back("printAxes");
	opt.allowed.push_back("printTermEnergies");
	opt.allowed.push_back("deleteTerminalHbonds");
	opt.allowed.push_back("linkInterfacialPositions");

	//Input Files
	opt.allowed.push_back("topFile");
	opt.allowed.push_back("parFile");
	opt.allowed.push_back("geometryDensityFile");
	opt.allowed.push_back("solvFile");
	opt.allowed.push_back("rotLibFile");
	opt.allowed.push_back("backboneCrd");
	opt.allowed.push_back("hbondFile");
	opt.allowed.push_back("pdbOutputDir");
	opt.allowed.push_back("infile");
	opt.allowed.push_back("selfEnergyFile");
	opt.allowed.push_back("pairEnergyFile");
	opt.allowed.push_back("sequenceEntropyFile");
	opt.allowed.push_back("AACompositionPenaltyFile");
	opt.allowed.push_back("configfile");

	opt.allowed.push_back("thread");

	//Alternate
	opt.allowed.push_back("Ids");

	//Command Line Arguments
	opt.allowed.push_back("runNumber");
	opt.allowed.push_back("useIMM1");

	//MonteCarlo Arguments
	opt.allowed.push_back("numStatesToSave");

	//RNG Arguments
	opt.allowed.push_back("useTimeBasedSeed");

	opt.allowed.push_back("energyLandscape");
	opt.allowed.push_back("useAlaAtCTerminus");
	opt.allowed.push_back("useBaseline");

	//SelfPairManager Arguments
	opt.allowed.push_back("runDEESingles");
	opt.allowed.push_back("runDEEPairs");
	opt.allowed.push_back("runSCMF");

	//Energy Terms to Output
	opt.allowed.push_back("monomerEnergyTerms");
	opt.allowed.push_back("monomerIMM1EnergyTerms");
	opt.allowed.push_back("dimerEnergyTerms");
	opt.allowed.push_back("energyLandscapeTerms");
	opt.allowed.push_back("energyTermsToOutput");

	opt.allowed.push_back("energyTermList");

	//Load Rotamers from SASA values (from sgfc)
	opt.allowed.push_back("useSasa");
	opt.allowed.push_back("sasaRepackLevel");
	opt.allowed.push_back("interfaceLevel");

	//Begin Parsing through the options
	OptionParser OP;
	OP.readArgv(_argc, _argv);
	OP.setDefaultArguments(opt.defaultArgs);
	OP.setRequired(opt.required);
	OP.setAllowed(opt.allowed);
	OP.autoExtendOptions();

	if (OP.countOptions() == 0){
		usage();
		opt.errorMessages += "No options given!\n";
		exit(0);
	}

	/*****************************************
	 *  CHECK THE GIVEN OPTIONS
	 *****************************************/
	if (!OP.checkOptions()) {
		opt.errorFlag = true;
		opt.OPerrors = OP.getErrors();
		return opt;
	}
	opt.errorFlag = false;
	opt.warningFlag = false;

	opt.errorMessages = "";
	opt.warningMessages = "";

	/*****************************************
	 *  CHECK THE GIVEN OPTIONS
	 *****************************************/
	opt.configfile = OP.getString("configfile");
	if (opt.configfile != "") {
		OP.readFile(opt.configfile);
		if (OP.fail()) {
			opt.errorFlag = true;
			opt.errorMessages += "Cannot read configuration file " + opt.configfile + "\n";
		}
	}

	opt.getGeoFromPDBData = OP.getBool("getGeoFromPDBData");
	if (OP.fail()) {
		opt.warningMessages += "getGeoFromPDBData not specified, defaulting to false\n";
		opt.warningFlag = true;
		opt.getGeoFromPDBData = false;
	}

	opt.runNumber = OP.getString("runNumber");
	if (OP.fail()) {
		opt.warningMessages += "runNumber not specified, using 1\n";
		opt.warningFlag = true;
		opt.runNumber = MslTools::intToString(1);
	}

	opt.useIMM1 = OP.getBool("useIMM1");
	if (OP.fail()) {
		opt.warningMessages += "useIMM1 not specified, defaulting to false\n";
		opt.warningFlag = true;
		opt.useIMM1 = false;
	}

	opt.deleteTerminalHbonds = OP.getBool("deleteTerminalHbonds");
	if (OP.fail()) {
		opt.deleteTerminalHbonds = true;
		opt.warningMessages += "deleteTerminalHbonds not specified using true\n";
		opt.warningFlag = true;
	}

	opt.tmStart = OP.getInt("tmStart");
	if(OP.fail()) {
		opt.warningMessages += "tmStart not specified using 1\n";
		opt.warningFlag = true;
		opt.tmStart = 1;
	}

	opt.tmEnd = OP.getInt("tmEnd");
	if(OP.fail()) {
		opt.tmEnd = opt.tmStart+opt.backboneLength;
		opt.warningMessages += "tmEnd not specified using " + MslTools::intToString(opt.tmStart+opt.backboneLength) + "\n";
		opt.warningFlag = true;
	}

	opt.startResNum = OP.getInt("startResNum");
	if (OP.fail()) {
		opt.warningMessages += "startResNum not specified using " + MslTools::intToString(opt.tmStart) + "\n";
		opt.warningFlag = true;
		opt.startResNum = opt.tmStart;
	}

	opt.endResNum = OP.getInt("endResNum");
	if (OP.fail()) {
		opt.warningMessages += "endResNum not specified using " + MslTools::intToString(opt.tmEnd) + "\n";
		opt.warningFlag = true;
		opt.endResNum = opt.tmEnd;
	}

	opt.xShift = OP.getDouble("xShift");
	if (OP.fail()) {
		opt.warningMessages += "xShift not specified, defaulting getGeoFromPDBData true\n";
		opt.warningFlag = true;
		opt.getGeoFromPDBData = true;
	}
	opt.zShift = OP.getDouble("zShift");
	if (OP.fail()) {
		opt.warningMessages += "zShift not specified, defaulting getGeoFromPDBData true\n";
		opt.warningFlag = true;
		opt.getGeoFromPDBData = true;
	}
	opt.axialRotation = OP.getDouble("axialRotation");
	if (OP.fail()) {
		opt.warningMessages += "axialRotation not specified, defaulting getGeoFromPDBData true\n";
		opt.warningFlag = true;
		opt.getGeoFromPDBData = true;
	}
	opt.crossingAngle = OP.getDouble("crossingAngle");
	if (OP.fail()) {
		opt.warningMessages += "crossingAngle not specified, defaulting getGeoFromPDBData true\n";
		opt.warningFlag = true;
		opt.getGeoFromPDBData = true;
	}

	opt.thread = OP.getInt("thread");
	if (OP.fail()) {
		opt.warningMessages += "thread not specified, defaulting to 0\n";
		opt.warningFlag = true;
		opt.thread = 0;
	}

	//Load Rotamers using SASA values (from sgfc)
	opt.useSasa = OP.getBool("useSasa");
	if (OP.fail()) {
		opt.warningMessages += "useSasa not specified, default true\n";
		opt.warningFlag = true;
	}
	opt.sasaRepackLevel = OP.getMultiString("sasaRepackLevel");
	if (OP.fail()) {
		opt.warningMessages += "sasaRepacklevel not specified! Default to one level at " + opt.SL;
		opt.sasaRepackLevel.push_back(opt.SL);
	}
	opt.interfaceLevel = OP.getInt("interfaceLevel");
	if (OP.fail()) {
		opt.warningMessages += "interfaceLevel not specified using 1\n";
		opt.warningFlag = true;
		opt.interfaceLevel = 1;
	}

	//Monte Carlo variables
	opt.MCCycles = OP.getInt("MCCycles");
	if (OP.fail()) {
		opt.errorMessages += "Number of MC cycles not specified!\n";
		opt.errorFlag = true;
	}

	opt.MCMaxRejects = OP.getInt("MCMaxRejects");
	if (OP.fail()) {
		opt.MCMaxRejects = 10;
		opt.warningMessages += "Number of MC max rejects not specified, default to using 10\n";
		opt.warningFlag = true;
	}

	opt.MCStartTemp = OP.getDouble("MCStartTemp");
	if (OP.fail()) {
		opt.warningMessages += "MCStartTemp not specified using 1000.0\n";
		opt.warningFlag = true;
		opt.MCStartTemp = 1000.0;
	}
	opt.MCEndTemp = OP.getDouble("MCEndTemp");
	if (OP.fail()) {
		opt.warningMessages += "MCEndTemp not specified using 0.5\n";
		opt.warningFlag = true;
		opt.MCEndTemp = 0.5;
	}
	opt.MCCurve = OP.getInt("MCCurve");
	if (OP.fail()) {
		opt.warningMessages += "MCCurve not specified using EXPONENTIAL(2)\n";
		opt.warningFlag = true;
		opt.MCCurve = 2;
	}

	opt.verbose = OP.getBool("verbose");
	if (OP.fail()) {
		opt.warningMessages += "verbose not specified using false\n";
		opt.warningFlag = true;
		opt.verbose = false;
	}
	opt.linkInterfacialPositions = OP.getBool("linkInterfacialPositions");
	if (OP.fail()) {
		opt.warningMessages += "linkInterfacialPositions not specified using true for less memory intensive version of code\n";
		opt.warningFlag = true;
		opt.linkInterfacialPositions = true;
	}
	opt.greedyCycles = OP.getInt("greedyCycles");
	if (OP.fail()) {
		opt.warningMessages += "greedyCycles not specified using 10\n";
		opt.warningFlag = true;
		opt.greedyCycles = 10;
	}

	opt.seed = OP.getInt("seed");
	if (OP.fail()) {
		opt.seed = 1;
		opt.warningMessages += "Seed not specified!\n";
		opt.warningFlag = true;
	}

	opt.weight_vdw = OP.getDouble("weight_vdw");
	if (OP.fail()) {
		opt.warningFlag = true;
		opt.warningMessages += "weight_vdw not specified, default 1.0\n";
		opt.weight_vdw = 1.0;
	}
	opt.weight_hbond = OP.getDouble("weight_hbond");
	if (OP.fail()) {
		opt.warningFlag = true;
		opt.warningMessages += "weight_hbond not specified, default 1.0\n";
		opt.weight_hbond = 1.0;
	}
	opt.weight_solv = OP.getDouble("weight_solv");
	if (OP.fail()) {
		opt.warningFlag = true;
		opt.warningMessages += "weight_solv not specified, default 1.0\n";
		opt.weight_solv = 1.0;
	}
	opt.weight_seqEntropy = OP.getDouble("weight_seqEntropy");
	if (OP.fail()) {
		opt.warningFlag = true;
		opt.warningMessages += "weight_seqEntropy not specified, default 1.0\n";
		opt.weight_seqEntropy = 1.0;
	}
	opt.weight_seqEntropy = opt.weight_seqEntropy;//Default allows 1 to be weighted equally to other energy terms (I should convert to actual weighting conversion used with other energy terms)

	//rotlevel
	opt.SL = OP.getString("SL");
	if (OP.fail()) {
		opt.warningFlag = true;
		opt.warningMessages += "SL not specified, default to SL70\n";
		opt.SL = "SL70.00";
	} else {
		opt.SL = "SL"+opt.SL;
	}
	opt.SLInterface = OP.getString("SLInterface");
	if (OP.fail()) {
		opt.warningFlag = true;
		opt.warningMessages += "SL not specified, default to SL70\n";
		opt.SL = "SL70.00";
	} else {
		opt.SLInterface = "SL"+opt.SLInterface;
	}

	opt.backboneAA = OP.getString("backboneAA");
	if (OP.fail()) {
		opt.warningFlag = true;
		opt.warningMessages += "backboneAA not specified, default to V\n";
		opt.backboneAA = "V";
	}
	opt.backboneLength = OP.getInt("backboneLength");
	if (OP.fail()) {
		opt.warningFlag = true;
		opt.warningMessages += "backboneLength not specified, default to 35\n";
		opt.backboneLength = 35;
	}

	opt.topFile = OP.getString("topFile");
	if (OP.fail()) {
		string envVar = "MSL_CHARMM_TOP";
		if(SYSENV.isDefined(envVar)) {
			opt.topFile = SYSENV.getEnv(envVar);
			opt.warningMessages += "topFile not specified using " + opt.topFile + "\n";
			opt.warningFlag = true;
		} else {
			opt.errorMessages += "Unable to determine topFile - " + envVar + " - not set\n"	;
			opt.errorFlag = true;
		}
	}

	opt.parFile = OP.getString("parFile");
	if (OP.fail()) {
		string envVar = "MSL_CHARMM_PAR";
		if(SYSENV.isDefined(envVar)) {
			opt.parFile = SYSENV.getEnv(envVar);
			opt.warningMessages += "parFile not specified using " + opt.parFile + "\n";
			opt.warningFlag = true;
		} else {
			opt.errorMessages += "Unable to determine parFile - " + envVar + " - not set\n"	;
			opt.errorFlag = true;
		}
	}

	opt.geometryDensityFile = OP.getString("geometryDensityFile");
	if (OP.fail()) {
		opt.warningMessages += "Unable to determine geometryDensityFile, defaulting to original density file\n";
		opt.warningFlag = true;
		opt.geometryDensityFile = "/exports/home/gloiseau/mslib/trunk_AS/designFiles/2021_09_28_geometryDensityFile.txt";
	}

	opt.solvFile = OP.getString("solvFile");
	if (OP.fail()) {
		string envVar = "MSL_CHARMM_SOLV";
		if(SYSENV.isDefined(envVar)) {
			opt.solvFile = SYSENV.getEnv(envVar);
			opt.warningMessages += "solvFile not specified using " + opt.solvFile + "\n";
			opt.warningFlag = true;
		} else {
			opt.errorMessages += "Unable to determine solvFile - " + envVar + " - not set\n";
			opt.errorFlag = true;
		}
	}
	opt.rotLibFile = OP.getString("rotLibFile");
	if (OP.fail()) {
		string envVar = "MSL_ROTLIB";
		if(SYSENV.isDefined(envVar)) {
			opt.rotLibFile = SYSENV.getEnv(envVar);
			opt.warningMessages += "rotLibFile not specified using " + opt.rotLibFile + ", defaulting to " + SYSENV.getEnv(envVar) + "\n";
			opt.warningFlag = true;
		} else {
			opt.errorMessages += "Unable to determine rotLibFile - " + envVar + " - not set\n";
			opt.errorFlag = true;
		}
	}

	opt.backboneCrd = OP.getString("backboneCrd");
	if (OP.fail()) {
		opt.errorMessages += "Unable to determine backboneCrd";
		opt.errorFlag = true;
	}

	opt.hbondFile = OP.getString("hbondFile");
	if (OP.fail()) {
		string envVar = "MSL_HBOND_CA_PAR";
		if(SYSENV.isDefined(envVar)) {
			opt.hbondFile = SYSENV.getEnv(envVar);
			opt.warningMessages += "hbondFile not specified using " + opt.hbondFile + "\n";
			opt.warningFlag = true;
		} else {
			opt.errorMessages += "Unable to determine hbondFile - MSL_HBOND_CA_PAR - not set\n"	;
			opt.errorFlag = true;
		}
	}

	opt.infile = OP.getString("infile");
	if (OP.fail()) {
		opt.warningMessages += "infile not specified, default to /data01/sabs/tmRepacks/pdbFiles/69-gly-residue-helix.pdbi\n";
		opt.warningFlag = true;
		opt.infile = "/data01/sabs/tmRepacks/pdbFiles/69-gly-residue-helix.pdb";
	}

	opt.selfEnergyFile = OP.getString("selfEnergyFile");
	if (OP.fail()) {
		opt.warningMessages += "selfEnergyFile not specified, default \n";
		opt.warningFlag = true;
		opt.selfEnergyFile = "/exports/home/gloiseau/mslib/trunk_AS/DesignFiles/2020_10_07_meanSelf_par.txt";
	}
	opt.pairEnergyFile = OP.getString("pairEnergyFile");
	if (OP.fail()) {
		opt.warningMessages += "pairEnergyFile not specified, default \n";
		opt.warningFlag = true;
		opt.pairEnergyFile = "/exports/home/gloiseau/mslib/trunk_AS/DesignFiles/2020_10_07_meanPair_par.txt";
	}
	opt.sequenceEntropyFile = OP.getString("seqEntropyFile");
	if (OP.fail()) {
		opt.warningMessages += "seqEntropyFile not specified, default to /data01/sabs/tmRepacks/pdbFiles/69-gly-residue-helix.pdbi\n";
		opt.warningFlag = true;
		opt.sequenceEntropyFile = "/exports/home/gloiseau/mslib/trunk_AS/myProgs/gloiseau/sequenceEntropies.txt";
	}
	opt.AACompositionPenaltyFile = OP.getString("AACompositionPenaltyFile");
	if (OP.fail()) {
		opt.warningMessages += "AACompositionPenaltyFile not specified, default \n";
		opt.warningFlag = true;
		opt.AACompositionPenaltyFile = "/exports/home/gloiseau/mslib/trunk_AS/DesignFiles/AACompositionPenalties.out";
	}

	opt.pdbOutputDir = OP.getString("pdbOutputDir");
	if (OP.fail()) {
		opt.errorMessages += "Unable to determine pdbOutputDir";
		opt.errorFlag = true;
	}

	opt.Ids = OP.getStringVector("Ids");
	if (OP.fail()) {
		opt.errorMessages += "Unable to identify alternate AA identities, make sure they are space separated\n";
		opt.errorFlag = true;
	}

	//MonteCarlo Options
	opt.numStatesToSave = OP.getInt("numStatesToSave");
	if (OP.fail()){
		opt.errorMessages += "numStatesToSave not specified, defaulting to 5";
		opt.warningFlag = true;
		opt.numStatesToSave = 5;
	}
	//SelfPairManager Optimization Options
	opt.runDEESingles = OP.getBool("runDEESingles");
	if (OP.fail()) {
		opt.warningMessages += "runDEESingles not specified, defaulting to false";
		opt.warningFlag = true;
		opt.runDEESingles = false;
	}
	opt.runDEEPairs = OP.getBool("runDEEPairs");
	if (OP.fail()) {
		opt.warningMessages += "runDEEPairs not specified, defaulting to false";
		opt.warningFlag = true;
		opt.runDEEPairs = false;
	}
	opt.runSCMF = OP.getBool("runSCMF");
	if (OP.fail()) {
		opt.warningMessages += "runSCMF not specified, defaulting to true";
		opt.warningFlag = true;
		opt.runSCMF = true;
	}

	opt.useTimeBasedSeed = OP.getBool("useTimeBasedSeed");
	if (OP.fail()) {
		opt.warningMessages += "useTimeBasedSeed not specified, defaulting to false";
		opt.warningFlag = true;
		opt.useTimeBasedSeed = false;
	}

	opt.energyLandscape = OP.getBool("energyLandscape");
	if (OP.fail()) {
		opt.warningMessages += "energyLandscape not specified, defaulting to false";
		opt.warningFlag = true;
		opt.energyLandscape = false;
	}

	opt.useAlaAtCTerminus = OP.getBool("useAlaAtCTerminus");
	if (OP.fail()) {
		opt.warningMessages += "useAlaAtCTerminus not specified, defaulting to false";
		opt.warningFlag = true;
		opt.useAlaAtCTerminus = false;
	}

	opt.useBaseline = OP.getBool("useBaseline");
	if (OP.fail()) {
		opt.warningMessages += "useBaseline not specified, defaulting to false";
		opt.warningFlag = true;
		opt.useBaseline = false;
	}
	//Energy Terms to Output
	opt.monomerEnergyTerms = OP.getStringVector("monomerEnergyTerms");
	if (OP.fail()) {
		opt.monomerEnergyTerms.push_back("Monomer");
		opt.monomerEnergyTerms.push_back("VDWMonomer");
		opt.monomerEnergyTerms.push_back("HbondMonomer");
		opt.monomerEnergyTerms.push_back("MonomerSelfBaseline");
		opt.monomerEnergyTerms.push_back("MonomerPairBaseline");
	}
	opt.monomerIMM1EnergyTerms = OP.getStringVector("monomerIMM1EnergyTerms");
	if (OP.fail()) {
		opt.monomerIMM1EnergyTerms.push_back("Monomerw/IMM1");
		opt.monomerIMM1EnergyTerms.push_back("VDWMonomerw/IMM1");
		opt.monomerIMM1EnergyTerms.push_back("HbondMonomerw/IMM1");
		opt.monomerIMM1EnergyTerms.push_back("IMM1Monomer");
	}
	opt.dimerEnergyTerms = OP.getStringVector("dimerEnergyTerms");
	if (OP.fail()) {
		opt.dimerEnergyTerms.push_back("Dimer");
		opt.dimerEnergyTerms.push_back("HbondDimer");
		opt.dimerEnergyTerms.push_back("VDWDimer");
		opt.dimerEnergyTerms.push_back("IMM1Dimer");
	}
	opt.energyLandscapeTerms = OP.getStringVector("energyLandscapeTerms");
	if (OP.fail()) {
		opt.energyLandscapeTerms.push_back("EnergyBeforeLocalMC");
		opt.energyLandscapeTerms.push_back("DimerNoIMM1");
		opt.energyLandscapeTerms.push_back("Baseline");
		opt.energyLandscapeTerms.push_back("VDWDimerNoIMM1");
		opt.energyLandscapeTerms.push_back("HBONDDimerNoIMM1");
		opt.energyLandscapeTerms.push_back("EnergyBeforeLocalMCw/seqEntropy");
	}
	opt.energyTermsToOutput = OP.getStringVector("energyTermsToOutput");
	if (OP.fail()) {
		opt.energyTermsToOutput.push_back("Total");
		opt.energyTermsToOutput.push_back("Dimer");
		opt.energyTermsToOutput.push_back("Monomer");
		opt.energyTermsToOutput.push_back("VDWDimer");
		opt.energyTermsToOutput.push_back("VDWMonomer");
		opt.energyTermsToOutput.push_back("VDWDiff");
		opt.energyTermsToOutput.push_back("HBONDDimer");
		opt.energyTermsToOutput.push_back("HBONDMonomer");
		opt.energyTermsToOutput.push_back("HBONDDiff");
		opt.energyTermsToOutput.push_back("IMM1Dimer");
		opt.energyTermsToOutput.push_back("IMM1Monomer");
		opt.energyTermsToOutput.push_back("IMM1Diff");
		opt.energyTermsToOutput.push_back("MonomerNoIMM1");
		opt.energyTermsToOutput.push_back("DimerNoIMM1");
		opt.energyTermsToOutput.push_back("Baseline");
		opt.energyTermsToOutput.push_back("Baseline-Monomer");
		opt.energyTermsToOutput.push_back("VDWDimerNoIMM1");
		opt.energyTermsToOutput.push_back("VDWMonomerNoIMM1");
		opt.energyTermsToOutput.push_back("HBONDDimerNOIMM1");
		opt.energyTermsToOutput.push_back("HBONDMonomerNOIMM1");
		opt.energyTermsToOutput.push_back("DimerSelfBaseline");
		opt.energyTermsToOutput.push_back("DimerPairBaseline");
	}
	opt.energyTermList = OP.getStringVector("energyTermList");
	if (OP.fail()) {
		//This works, but I think if you ever want to output more terms in the future, need to add them to the terms above
		//TODO: write in an error that will tell you if the above is the case
		opt.energyTermList.push_back("CHARMM_VDW");
		opt.energyTermList.push_back("SCWRL4_HBOND");
		opt.energyTermList.push_back("CHARMM_IMM1");
		opt.energyTermList.push_back("CHARMM_IMM1REF");
	}

	opt.rerunConf = OP.getConfFile();

	return opt;
}
