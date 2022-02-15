/**
 * @Author: Gilbert Loiseau
 * @Date:   2022/02/11
 * @Email:  gjowl04@gmail.com
 * @Filename: seqDesign.cpp
 * @Last modified by:   Gilbert Loiseau
 * @Last modified time: 2022/02/14
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
#include "design.h"
#include "design_options.h"
//#include "seqDesign.h"

//write in more includes here for functions files: https://www.youtube.com/watch?v=47sZhrJ1USY&ab_channel=EricLiang


using namespace MSL;
using namespace std;

static SysEnv SYSENV;
//string programName = "seqDesign";//TODO: better name
//string programDescription = "Designs sequences for backbone geometries extracted from the PDB, "
//"optimizing specifically for vdW energies";
//string programAuthor = "Gilbert Loiseau";
//string programVersion = "2";
//string programDate = "11 February 2022";
//string mslVersion = MSLVERSION;
//string mslDate = MSLDATE;

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

///***********************************
// *geometry
// ***********************************/
////CATM Functions
//void c2Symmetry(AtomPointerVector & _apvA, AtomPointerVector & _apvB);
//void moveZCenterOfCAMassToOrigin(AtomPointerVector& _apV, AtomPointerVector& _axis, Transforms & _trans);
//void transformation(AtomPointerVector & _chainA, AtomPointerVector & _chainB, AtomPointerVector & _axisA, AtomPointerVector & _axisB, CartesianPoint & _ori, CartesianPoint & _xAxis, CartesianPoint & _zAxis, double _zShift, double _axialRotation, double _crossingAngle, double _xShift, Transforms & _trans);
//void backboneMovement(AtomPointerVector & _chainA, AtomPointerVector & _chainB, AtomPointerVector & _axisA, AtomPointerVector & _axisB, Transforms _trans, double _deltaMove, unsigned int moveType);
//void xShiftTransformation(AtomPointerVector & _chainA, AtomPointerVector & _chainB, AtomPointerVector & _axisA, AtomPointerVector & _axisB, double _xShift, Transforms & _trans);
//void readGeometryFile(string _filename, vector<string>& _fileVec);
//void getGeometry(Options &_opt, RandomNumberGenerator &_RNG, vector<double> &_densities, ofstream &_out);
//
///***********************************
// *string output
// ***********************************/
//// TODO: if possible, make some of these more multipurpose and change names, and add in one or two line examples for what they do
//string convertToPolymerSequenceNeutralPatch(string _seq, int _startResNum);
//string convertToPolymerSequenceNeutralPatchMonomer(string _seq, int _startResNum);
//string convertPolymerSeqToOneLetterSeq(Chain &_chain);
//string generateString(string _backbone, int _length);
//string generateBackboneSequence(string _backbone, int _length);
//string generateMonomerMultiIDPolymerSequence(string _seq, int _startResNum, vector<string> _alternateIds, vector<int> _interfacialPositions);
//string generatePolymerSequence(string _backboneAA, int _backboneLength, int _startResNum);
//string generateMonomerPolymerSequenceFromSequence(string _sequence, int _startResNum);
//string generateMultiIDPolymerSequence(string _seq, int _startResNum, vector<string> _alternateIds, vector<int> _interfacialPositions);
//string getInterfaceString(vector<int> _interface, int _seqLength);
//string getAlternateIdString(vector<string> _alternateIds);
//string getInterfaceSequence(Options &_opt, string _interface, string _sequence);
//
///***********************************
// *repack functions
// ***********************************/
//void repackSideChains(SelfPairManager & _spm, int _greedyCycles);
//std::vector < std::vector < bool > > getActiveMask (System &_sys);
//
///***********************************
// *define interface and rotamer sampling
// ***********************************/
//vector<int> getRotamerSampling(string _rotamerLevels);
//vector<int> getLinkedPositions(vector<int> _rotamerSampling, int _interfaceLevel, int _highestRotamerLevel);
//vector<uint> getVariablePositions(vector<int> &_interfacialPositions);
//vector<vector<string>> convertToLinkedFormat(System &_sys, vector<int> &_interfacialPositions, int _backboneLength);
//std::vector<pair <int, double> > calculateResidueBurial (System &_sys);
//std::vector<pair <int, double> > calculateResidueBurial (System &_sys, Options &_opt, string _seq);
////TODO: change all of the original interfacePositions to variablePositions and the allInterfacePositions to interfacePositions
//void defineInterfaceAndRotamerSampling(Options &_opt, PolymerSequence _PS, string &_rotamerLevels, string &_polySeq, string &_variablePositionString, string &_rotamerSamplingString, vector<int> &_linkedPositions, vector<uint> &_interfacePositions, vector<uint> &_variablePositions, vector<int> &_rotamerSamplingPerPosition, ofstream &_out, string _axis);
//
///***********************************
// *output file functions
// ***********************************/
//void setupDesignDirectory(Options &_opt, string _date);
//void printConfigFile(Options & _opt, ofstream & _out);
//void outputEnergyFile(Options &_opt, string _interface, vector<string> _allDesigns);
//void makeRepackConfig(Options &_opt, string _sequence, string _designDir, string _designNumber, string _pdbPath, string _crdPath, map<string,double> _energyMap);
//void makeDockingConfig(Options &_opt, string _sequence, vector<uint> _state, string _pdbPath, map<string,double> _energyMap, vector<int> _rotamerSampling);
//void outputRepackFile(Options &_opt, vector<string> _dockingDesigns);
//void outputDesignFiles(Options &_opt, string _interface, vector<int> _rotamerSampling, vector<pair<string,vector<uint>>> _sequenceStatePair, map<string,map<string,double>> _sequenceEnergyMap, vector<double> _densities);
//
///***********************************
// *load rotamer functions
// ***********************************/
//void loadMonomerRotamers(System &_sys, SystemRotamerLoader &_sysRot);
//void loadRotamersBySASABurial(System &_sys, SystemRotamerLoader &_sysRot, Options &_opt, vector<int> &_rotamerSampling);
//void loadInterfacialRotamers(System &_sys, SystemRotamerLoader &_sysRot, string _SL, int _numRotamerLevels, vector<int> _interface);
//void loadRotamers(System &_sys, SystemRotamerLoader &_sysRot, string _SL);
//void loadRotamers(System &_sys, SystemRotamerLoader &_sysRot, Options &_opt, vector<int> &_rotamerSampling);//Uses rotamer sampling defined by SASA values to load rotamers by position
//void loadRotamersSPM(System &_sys, SystemRotamerLoader &_sysRot, Options &_opt);
//
///***********************************
// *baseline energy helper functions
// ***********************************/
//vector<double> calcBaselineEnergies(System &_sys, int _seqLength);
//vector<double> calcPairBaselineEnergies(System &_sys, int _seqLength);
//double sumEnergyVector(vector<double> _energies);
//
///***********************************
// *calculate energies
// ***********************************/
//void computeDimerEnergy(System &_sys, Options& _opt, map<string,map<string,double>> &_sequenceEnergyMap, string &_sequence, vector<uint> &_stateVec, vector<int> &_rotamerSampling, vector<vector<string>> &_linkedPos, int _seqNumber, RandomNumberGenerator &_RNG, PDBWriter &_writer, ofstream &_sout, ofstream &_err);
//void computeDimerEnergiesLinked(System &_sys, Options &_opt, map<string,map<string,double>> &_sequenceEnergyMap, vector<pair<string,vector<uint>>> &_sequenceStatePair, vector<int> &_rotamerSampling, vector<vector<string>> &_linkedPos, RandomNumberGenerator &_RNG, PDBWriter &_writer, ofstream &_sout, ofstream &_err);
//void computeDimerEnergies(System &_sys, Options &_opt, map<string, map<string,double>> &_sequenceEnergyMap, vector<pair<string,vector<uint>>> &_sequenceStatePair, vector<int> _rotamerSamplingPerPosition, vector<vector<string>> &_linkedPos, RandomNumberGenerator &_RNG, ofstream &_sout, ofstream &_err);
//void computeMonomerEnergyNoIMM1(Options& _opt, map<string,map<string,double>> &_sequenceEnergyMap, string &_seq, RandomNumberGenerator &_RNG, ofstream &_sout, ofstream &_err);
//void computeMonomerEnergyIMM1(Options& _opt, Transforms & _trans, map<string,map<string,double>> &_sequenceEnergyMap, string _seq, RandomNumberGenerator &_RNG, ofstream &_sout, ofstream &_err);
//void computeMonomerEnergies(Options &_opt, Transforms &_trans, map<string, map<string,double>> &_sequenceEnergyMap, vector<string> &_seqs, RandomNumberGenerator &_RNG, ofstream &_sout, ofstream &_err);
//
///***********************************
// *other helper functions
// ***********************************/
//void saveEnergyDifference(Options _opt, map<string,map<string,double>> &_sequenceEnergyMap, string _sequence);
//void outputEnergiesByTerm(SelfPairManager &_spm, vector<uint> _stateVec, map<string,double> &_energyMap, vector<string> _energyTermList, string _energyDescriptor, bool _includeIMM1);
//void outputEnergiesByTermLinked(EnergySet *_Eset, map<string,double> &_energyMap, vector<string> _energyTermList, string _energyDescriptor);
//void deleteTerminalHydrogenBondInteractions(System &_sys, Options &_opt);
//map<string, double> readSingleParameters(string _baselineFile);
//map<string,map<string,map<uint, double>>> readPairParameters(string _baselineFile);
//
///***********************************
// *energy builders
// ***********************************/
//void buildBaselineIMM1Interactions(System &_sys, map<string, double> &_selfMap);
//void buildSelfInteractions(System &_sys, map<string, double> &_selfMap);
//void buildPairInteractions(System &_sys, map<string,map<string,map<uint,double>>>& _pairMap);
//void buildSequenceEntropy(System &_sys, map<string, double> &_sequenceEntropyMap, double _weight);
//
///***********************************
// *stateMC helper functions
// ***********************************/
////gets a random position and chooses a random rotamer
//void randomPointMutation(System &_sys, Options &_opt, RandomNumberGenerator &_RNG, vector<uint> _variablePositions, vector<string> &_ids);
//void randomPointMutationUnlinked(System &_sys, Options &_opt, RandomNumberGenerator &_RNG, vector<uint> _variablePositions, vector<string> &_ids);
//void randomRotamerChange(System &_sys, Options &_opt, RandomNumberGenerator &_RNG, vector<uint> _variablePositions, vector<unsigned int> &_stateVec);
//void randomRotamerChangeNonLinked(System &_sys, Options &_opt, RandomNumberGenerator &_RNG, map<int,map<int,pair<uint,uint>>> &_posRotLimitMap, vector<uint> _variablePositions, vector<unsigned int> &_stateVec);
//void sameSequenceChecker(string &_newSeq, vector<string> &_seqs);
//bool sameSequenceChecker(string &_newSeq, double &_newEnergy, vector<uint> &_state, vector<pair<double,string>> &_enerSeqPair, vector<pair<double,vector<uint>>> &_energyStateVec);
//double getMapValueFromKey(map<string,double> &_map, string _key);//TODO: move funciton to appropriate spot
//void saveSequence(Options &_opt, vector<pair<double,string>> &_energyVector, vector<pair<double,vector<uint>>> &_energyStateVec, string _sequence, vector<uint> _state, double _energy);
//void saveSequence(Options &_opt, RandomNumberGenerator &_RNG, map<vector<uint>, map<string,double>> &_stateEnergyMap, vector<pair<double,string>> &_energyVector, vector<pair<double,vector<uint>>> &_energyStateVec, string _sequence, vector<uint> _state, double _energy, ofstream &_out);
//map<int,map<int,pair<uint, uint>>> setupRotamerPositionMap(System &_sys, vector<uint> _interfacialPositionsList);
//void unlinkBestState(Options &_opt, vector<uint> &_bestState, vector<int> _linkedPositions, int _backboneLength);
//bool convertStateMapToSequenceMap(System &_sys, vector<pair<double,vector<uint>>> &_energyStateVec, map<vector<uint>, map<string,double>> &_stateEnergyMap, map<string, map<string,double>> &_sequenceEnergyMap, vector<pair<string,vector<uint>>> &_sequenceStatePair, ofstream &_out);
//
///***********************************
// *sequence entropy functions
// ***********************************/
//map<string,int> getAACountMap(vector<string> _seq);
//double calcNumberOfPermutations(map<string,int> _seqAACounts, int _seqLength);
//void interfaceAASequenceEntropySetup(string _seq, map<string,int> &_seqCountMap, double &_numberOfPermutations, vector<uint> _interfacialPositionsList);
//void internalAASequenceEntropySetup(string _seq, map<string,int> &_seqCountMap, double &_numberOfPermutations, int _seqLength);
//void sequenceEntropySetup(string _seq, map<string,int> &_seqCountMap, double &_numberOfPermutations, int _seqLength);
//double calculateSequenceProbability(map<string,int> &_seqCountMap, map<string,double> &_entropyMap, double _numberOfPermutations);
////double getSequenceEntropyProbability(Options &_opt, string _sequence, map<string,double> _entropyMap);
////double getInterfaceSequenceEntropyProbability(Options &_opt, string _sequence, map<string,double> &_entropyMap, vector<uint> _interfacialPositionsList);
//void calculateInterfaceSequenceEntropy(Options &_opt, string _prevSeq, string _currSeq, map<string,double> _entropyMap, double &_prevSEProb, double &_currSEProb, double &_prevEntropy, double &_currEntropy, double _bestEnergy, double _currEnergy, double &_bestEnergyTotal, double &_currEnergyTotal, vector<uint> _interfacePositionsList);
//void calculateSequenceEntropy(Options &_opt, string _prevSeq, string _currSeq, map<string,double> _entropyMap, double &_prevSEProb, double &_currSEProb, double &_prevEntropy, double &_currEntropy, double _bestEnergy, double _currEnergy, double &_bestEnergyTotal, double &_currEnergyTotal);
//
//// other functions
//double getStandardNormal(RandomNumberGenerator& RNG);
//void checkIfAtomsAreBuilt(System &_sys, ofstream &_err);
//void addSequencesToVector(vector<pair<double,string>> &_energyVector, vector<string> &_allSeqs);
//
///***********************************
// *MonteCarlo functions
// ***********************************/
//// Linked version of the state monte carlo
//void stateMCLinked(System &_sys, SelfPairManager &_spm, Options &_opt, PolymerSequence &_PS, map<string, map<string,double>> &_sequenceEnergyMap, map<string,double> &_sequenceEntropyMap, vector<unsigned int> &_bestState, vector<string> &_seqs, vector<string> &_allSeqs, vector<pair<string,vector<uint>>> &_sequenceStatePair, vector<uint> &_interfacialPositionsList, vector<int> &_rotamerSampling, vector<vector<string>> &_linkedPos, RandomNumberGenerator &_RNG, ofstream &_sout, ofstream &_err);
//void getEnergiesForStartingSequence(Options &_opt, SelfPairManager &_spm, string _startSequence, vector<unsigned int> &_stateVector, map<string, map<string, double>> &_sequenceEnergyMap, map<string, double> &_entropyMap);
//// Unlinked version of the state monte carlo
//void stateMCUnlinked(System &_sys, Options &_opt, PolymerSequence &_PS, map<string, map<string,double>> &_sequenceEnergyMap, map<string,double> &_sequenceEntropyMap, vector<unsigned int> &_bestState, vector<string> &_seqs, vector<string> &_allSeqs, vector<pair<string,vector<uint>>> &_sequenceStatePair, vector<uint> &_interfacialPositionsList, vector<uint> &_variablePositionsList, vector<int> &_rotamerSampling, vector<vector<string>> &_linkedPos, RandomNumberGenerator &_RNG, ofstream &_sout, ofstream &_err);
//void getTotalEnergyAndWritePdbs(System &_sys, Options &_opt, map<string, map<string,double>> &_sequenceEnergyMap, string _sequence, vector<uint> _stateVec, vector<int> _rotamerSampling, RandomNumberGenerator &_RNG, int _seqNumber, PDBWriter &_writer, ofstream &_sout, ofstream &_err);
//vector<uint> getAllInterfacePositions(Options &_opt, vector<int> &_rotamerSamplingPerPosition);
//vector<uint> getInterfacePositions(Options &_opt, vector<int> &_rotamerSamplingPerPosition);
//void getDimerSasaScores(System &_sys, vector<pair<string,vector<uint>>> &_sequenceStatePair, map<string, map<string,double>> &_sequenceEnergyMap);
//void getSasaDifference(vector<pair<string,vector<uint>>> &_sequenceStatePair, map<string, map<string,double>> &_sequenceEnergyMap);
//void getSasaForStartingSequence(System &_sys, string _sequence, vector<uint> _state, map<string, map<string,double>> &_sequenceEnergyMap);


//TODO: I may have to end up keeping all of the functions that use options in here (or change the way they work; if they only use one option, all good. If not, could keep it in here to keep it simple)
// Otherwise I may have to just initialize all of them as not options? unless I can pull in a structure of options into the h file ... right now I'm getting an undefined reference problem for options without the struct here
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
	ofstream sout;
	ofstream err;
	ofstream rerun;

	setupDesignDirectory(opt, date);

	string soutfile = opt.pdbOutputDir + "/summary.out";
	string errfile  = opt.pdbOutputDir + "/errors.out";
	string rerunfile = opt.pdbOutputDir + "/rerun.config";

	sout.open(soutfile.c_str());
	err.open(errfile.c_str());
	rerun.open(rerunfile.c_str());

	sout << date << endl;
	err << date << endl;


	/******************************************************************************
	 *               === LOAD RANDOM GEOMETRY FROM GEOMETRY FILE ===
	 ******************************************************************************/
	RandomNumberGenerator RNG;
	if (opt.useTimeBasedSeed){
		RNG.setTimeBasedSeed();
	} else {
		RNG.setSeed(opt.seed);
	}

	vector<double> densities;
	if (opt.getGeoFromPDBData){
		getGeometry(opt, RNG, densities, sout);
	}

	// Output Geometry
	cout << "***STARTING GEOMETRY:***" << endl;
	cout << "xShift:        " << opt.xShift << "\tDensity: " << densities[0] << endl;
	cout << "crossingAngle: " << opt.crossingAngle << "\tDensity: " << densities[0] << endl;
	cout << "axialRotation: " << opt.axialRotation << "\tDensity: " << densities[1] << endl;
	cout << "zShift:        " << opt.zShift << "\tDensity: " << densities[2] << endl << endl;

	//String for the alternateIds at the interface
	string alternateIds = getAlternateIdString(opt.Ids);
	cout << "Amino acids for design: LEU " << alternateIds << endl;

	rerun << opt.rerunConf << endl;
	rerun.close();

	/******************************************************************************
	 *                         === GENERATE POLYGLY ===
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
	vector<int> linkedPositions;
	vector<uint> interfacePositions;
	vector<uint> allInterfacePositions;
	vector<int> rotamerSamplingPerPosition;

	// Defines the interfacial positions and the number of rotamers to give each position
	defineInterfaceAndRotamerSampling(opt, PS, rotamerLevels, polySeq, variablePositionString, rotamerSamplingString, linkedPositions, allInterfacePositions, interfacePositions, rotamerSamplingPerPosition, sout, axis);

	/******************************************************************************
	 *         === COPY BACKBONE COORDINATES AND TRANSFORM TO GEOMETRY ===
	 ******************************************************************************/
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
	System sys;
	CharmmSystemBuilder CSB(sys, opt.topFile, opt.parFile, opt.solvFile);
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
	sys.assignCoordinates(pdb.getAtomPointers(),false);
	sys.buildAllAtoms();

	SystemRotamerLoader sysRot(sys, opt.rotLibFile);
	sysRot.defineRotamerSamplingLevels();

	// Add hydrogen bond term
	HydrogenBondBuilder hb(sys, opt.hbondFile);
	hb.buildInteractions(50);//when this is here, the HB weight is correct

	/******************************************************************************
	 *                     === INITIAL VARIABLE SET UP ===
	 ******************************************************************************/
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
	Eset->setWeight("CHARMM_VDW", 1);
	Eset->setWeight("SCWRL4_HBOND", 1);
	Eset->setWeight("CHARMM_IMM1REF", 1);
	Eset->setWeight("CHARMM_IMM1", 1);

	/******************************************************************************
	 *                === DELETE TERMINAL HYDROGEN BOND INTERACTIONS ===
	 ******************************************************************************/
	deleteTerminalHydrogenBondInteractions(sys,opt);

	/******************************************************************************
	 *                === CHECK TO SEE IF ALL ATOMS ARE BUILT ===
	 ******************************************************************************/
	checkIfAtomsAreBuilt(sys, err);

	/******************************************************************************
	 *                     === ADD IN BASELINE ENERGIES ===
	 ******************************************************************************/
	if (opt.useBaseline){
		//addBaselineToSelfPairManager();//TODO: was going to make this a function but I feel like it already exists in spm, so going to wait when I have time to look that up
		//initialize baseline maps to calculate energy for each sequence for comparison in baselineMonomerComparison_x.out
		map<string, double> selfMap = readSingleParameters(opt.selfEnergyFile);
		map<string,map<string,map<uint,double>>> pairMap = readPairParameters(opt.pairEnergyFile);
		buildSelfInteractions(sys, selfMap);
		buildPairInteractions(sys, pairMap);
		//sys.calcEnergy();
	}

	vector<vector<string>> linkedPos = convertToLinkedFormat(sys, linkedPositions, opt.backboneLength);
	sys.setLinkedPositions(linkedPos);

	//TODO: make this dynamic based on the list of AAs given
	// Get sequence entropy map
	map<string, double> sequenceEntropyMap = readSingleParameters(opt.sequenceEntropyFile);

	//make into a function
	//decided to try loading low number of rotamers for this instead of high
	loadRotamers(sys, sysRot, opt, rotamerSamplingPerPosition);
	//loadRotamersSPM(sys, sysRot, opt);
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

	time(&spmStart);
	spm.runOptimizer();
	time(&spmEnd);

	spmTime = difftime (spmEnd, spmStart);
	vector<unsigned int> initialState = spm.getSCMFstate();
	vector<unsigned int> bestState = spm.getBestSCMFBiasedMCState();
	vector<unsigned int> startingState = bestState;
	double bestEnergy = spm.getStateEnergy(bestState);
	double hbondEnergy = spm.getStateEnergy(bestState, "SCWRL4_HBOND");
	double vdwEnergy = spm.getStateEnergy(bestState, "CHARMM_VDW");


	sys.setActiveRotamers(initialState);
	string initialSeq = convertPolymerSeqToOneLetterSeq(sys.getChain("A"));
	sys.setActiveRotamers(bestState);
	string SCMFBestSeq = convertPolymerSeqToOneLetterSeq(sys.getChain("A"));
	sys.calcEnergy();
	string startSequence = SCMFBestSeq;//used for outputting starting sequence

	// TODO: make into a function?
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
	vector<string> seqs;
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
	// Initialize PDBWriter for design
	PDBWriter writer;
	writer.open(opt.pdbOutputDir + "/allDesigns.pdb");
	sout << "Calculating Final Energies..." << endl;
	for (uint i=0; i<sequenceStatePair.size(); i++){
		string sequence = sequenceStatePair[i].first;
		vector<uint> state = sequenceStatePair[i].second;
		sout << "Sequence " << i+1 << ": " << sequence << endl;
		int seqNumber = i;
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
	opt.allowed.push_back("sequenceStart");
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
	opt.allowed.push_back("dockingEnergyCutoff");

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
	opt.allowed.push_back("selfEnergyFileSPM");
	opt.allowed.push_back("pairEnergyFileSPM");
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

	opt.sequence = OP.getString("sequence");
	if(OP.fail()) {
		opt.warningMessages += "sequence not specified using L\n";
		opt.warningFlag = true;
		opt.sequence = "L";
	}

	opt.sequenceLength = OP.getInt("sequenceLength");
	if(OP.fail()) {
		opt.warningMessages += "sequenceLength not specified using 21\n";
		opt.warningFlag = true;
		opt.sequenceLength = 21;
	}


	opt.tmStart = OP.getInt("tmStart");
	if(OP.fail()) {
		opt.warningMessages += "tmStart not specified using 1\n";
		opt.warningFlag = true;
		opt.tmStart = 1;
	}

	opt.tmEnd = OP.getInt("tmEnd");
	if(OP.fail()) {
		opt.tmEnd = opt.tmStart+opt.sequenceLength;
		opt.warningMessages += "tmEnd not specified using " + MslTools::intToString(opt.tmStart+opt.sequenceLength) + "\n";
		opt.warningFlag = true;
	}

	opt.sequenceStart = OP.getInt("sequenceStart");
	if (OP.fail()) {
		opt.warningMessages += "sequenceStart not specified using 1\n";
		opt.warningFlag = true;
		opt.sequenceStart = 1;
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

	opt.transform = OP.getBool("transform");
	if (OP.fail()) {
		opt.warningMessages += "transform not specified, defaulting to false\n";
		opt.warningFlag = true;
		opt.transform = false;
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

	opt.repackEnergyCutoff = OP.getDouble("repackEnergyCutoff");
	if (OP.fail()) {
		opt.warningMessages += "repackEnergyCutoff not specified using 5.0\n";
		opt.warningFlag = true;
		opt.repackEnergyCutoff = 5.0;
	}
	opt.vdwEnergyCutoff = OP.getDouble("vdwEnergyCutoff");
	if (OP.fail()) {
		opt.warningMessages += "vdwEnergyCutoff not specified, defaulting to 0\n";
		opt.warningFlag = true;
		opt.vdwEnergyCutoff = 0;
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
	opt.selfEnergyFileSPM = OP.getString("selfEnergyFileSPM");
	if (OP.fail()) {
		opt.warningMessages += "selfEnergyFileSPM not specified, default \n";
		opt.warningFlag = true;
		opt.selfEnergyFileSPM = "/exports/home/gloiseau/mslib/trunk_AS/DesignFiles/2020_10_07_meanSelf_par.txt";
	}
	opt.pairEnergyFileSPM = OP.getString("pairEnergyFileSPM");
	if (OP.fail()) {
		opt.warningMessages += "pairEnergyFileSPM not specified, default \n";
		opt.warningFlag = true;
		opt.pairEnergyFileSPM = "/exports/home/gloiseau/mslib/trunk_AS/DesignFiles/2020_10_07_meanPair_par.txt";
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
