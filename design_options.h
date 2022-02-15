/**
 * @Author: Gilbert Loiseau
 * @Date:   2022/02/13
 * @Email:  gjowl04@gmail.com
 * @Filename: design_options.h
 * @Last modified by:   Gilbert Loiseau
 * @Last modified time: 2022/02/14
 */

#ifndef DESIGN_OPTIONS_H
#define DESIGN_OPTIONS_H

#include <sstream>
#include <vector>

using namespace std;

/******************************************
 *
 *  =======  OPTIONS =======
 *
 ******************************************/
 //TODO: simplify these options and have comments for each
struct Options{
	// input files
	string backboneCrd;
	string pdbOutputDir;
	string topFile;
	string parFile;
	string geometryDensityFile;
	string solvFile;
	string hbondFile;
	string rotLibFile;
	string infile;
	string selfEnergyFile;
	string pairEnergyFile;
	string selfEnergyFileSPM;
	string pairEnergyFileSPM;
	string sequenceEntropyFile;
	string AACompositionPenaltyFile;

	// sequence parameters
	string sequence;
	int sequenceLength;
	string backboneAA;
	int backboneLength;

	// booleans
	bool getGeoFromPDBData; //TRUE: randomly choose a dimeric geometry from the membrane protein pdb landscape OR FALSE: use a given dimer geometry
	bool verbose; //TRUE: write more outputs throughout the run
	bool deleteTerminalHbonds; //TRUE: delete hydrogen bonds at the termini OR FALSE: keep hydrogen bonds at termini
	bool linkInterfacialPositions; //TRUE: keeps interfacial positions linked when searching for the best states in stateMC (less memory) OR FALSE: unlinks positions (memory intensive)
	bool useSasa; //TRUE: solvent accessible surface area used to choose the number rotamers at each position OR FALSE: give a set number of rotamers to interface vs non-interface
	bool useTimeBasedSeed; //TRUE: use time based seed for RandomNumberGenerator OR FALSE: use given seed
	bool energyLandscape; //TRUE: collect all sequences and their respective monomer and dimer energies
	bool useAlaAtCTerminus; //TRUE: use ALA at C terminus of sequence FALSE: use LEU at C terminus
	bool useBaseline; //TRUE: use  TODO...
	bool useIMM1;

	// repack parameters
	int greedyCycles;
	int seed;

	// load rotamers useSasa = false
	string SL; //number of rotamers
	string SLInterface; //number of rotamers for interfacial AAs
	// load rotamers useSasa = true
	std::vector<string> sasaRepackLevel;
	int interfaceLevel;

	// tm
	int tmStart;
	int tmEnd;

	// the actual AAs being modeled
	int startResNum;
	int endResNum;
	int sequenceStart;

	// Starting Geometry
	double xShift;
	double zShift;
	double crossingAngle;
	double axialRotation;
	bool transform;

	// crossing point
	int thread;

	// Monte Carlo parameters
	int MCCycles;
	int MCMaxRejects;
	double MCStartTemp;
	double MCEndTemp;
	int MCCurve;

	double repackEnergyCutoff;
	double vdwEnergyCutoff;

	// energy weights
	double weight_vdw;
	double weight_hbond;
	double weight_solv;
	double weight_seqEntropy;

	// alternate identities
	vector<string> Ids;

	// state Monte Carlo Options
	int numStatesToSave;

	// energy terms to output
	vector<string> monomerEnergyTerms;
	vector<string> monomerIMM1EnergyTerms;
	vector<string> dimerEnergyTerms;
	vector<string> energyLandscapeTerms;
	vector<string> energyTermsToOutput;
	vector<string> energyTermList;

	//SelfPairManager Options
	bool runDEESingles;
	bool runDEEPairs;
	bool runSCMF;

	string configfile;
	string runNumber;

	/***** MANAGEMENT VARIABLES ******/
	string pwd; // the present working directory obtained with a getenv
	string host; // the host name obtained with a getenv
	bool version; // ask for the program version
	bool help; // ask for the program help

	bool errorFlag; // true if there are errors
	bool warningFlag; // true if there are warnings
	string errorMessages; // error messages
	string warningMessages; //warning messages

	vector<string> allowed; //list of allowed options
	vector<string> required; //list of required options

	vector<string> disallowed;  // disallowed options that were given
	vector<string> missing; // required options that were not given
	vector<string> ambiguous; // required options that were not given
	vector<string> defaultArgs; // the default arguments can be specified in command line without "--option"
	vector<vector<string> > equivalent; // this links short options to long ones (for example -x can be given for --extended)

	string OPerrors; //the errors from the option parser
	string rerunConf; // data for a configuration file that would rerun the job as the current run
};

#endif
