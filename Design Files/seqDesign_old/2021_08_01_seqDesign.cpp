#include <fstream>
#include <sstream>
#include <iterator>

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
#include "BaselinePairInteraction.h"
#include "BaselineOuterPairInteraction.h"
#include "BaselineAAComposition.h"
#include "BaselineSequenceEntropy.h"
#include "BaselineSequenceEntropyNormalized.h"
#include "BaselinePermutation.h"
#include "SasaCalculator.h"

using namespace MSL;
using namespace std;

static SysEnv SYSENV;
string programName = "seqDesign";
string programDescription = "This is the most updated version of seqDesign: aims to design sequences from geometric data from the PDB optimizing specifically for vdW energies";
string programAuthor = "Gilbert Loiseau";
string programVersion = "1";
string programDate = "14 October 2020";
string mslVersion = MSLVERSION;
string mslDate = MSLDATE;

time_t startTime, endTime, spmStart, spmEnd;
double diffTime, spmTime;

/******************************************
 *  
 *  =======  OPTIONS =======
 *
 ******************************************/
struct Options{
	string sequence;
	int sequenceLength;
	string backboneAA;
	int backboneLength;

	// optional
	bool useGeoFromPDBData;

	// tm
	int tmStart;
	int tmEnd;

	// the actual AAs being modeled
	int startResNum;
	int endResNum;
	int sequenceStart;

	bool deleteTerminalHbonds;
	
	string SL; //number of rotamers
	string SLInterface; //number of rotamers

	// transformation
	double xShift;
	double zShift;
	double crossingAngle;
	double axialRotation;
	bool transform;
	int thread;
	int bbThread;

	// input files
	string backboneCrd;
	string pdbOutputDir;
	string topFile;
	string parFile;
	string baselineFile;
	string geometryDensityFile;
	string solvFile;
	string hBondFile;
	string rotLibFile;
	string monoRotLibFile;
	string infile;
	string kdeFile;
	string selfEnergyFile;
	string pairEnergyFile;
	string seqEntropyFile;
	string AACompositionPenaltyFile;

	// side-chain repack variable
	int MCCycles;
	int MCMaxRejects;
	double MCStartTemp;
	double MCEndTemp;
	int MCCurve;

	double deltaZ;
	double deltaAx;
	double deltaCross;
	double deltaX;

	bool verbose;
	int greedyCycles;
	int seed;
	int pairDist;

	int numberOfStructuresToMCRepack;
	double energyCutOff;
	
	// weights
	double weight_vdw;
	double weight_hbond;
	double weight_solv;
	double weight_seqEntropy;
	
	// input monomerEnergy
	bool inputMonomerE;
	int monoE_vdw;
	int monoE_hbond;
	int monoE_solv;
	int monoE_solvRef;

	// clustering options (optional)
	bool printAllCrds;
	bool printAxes;
	bool printTermEnergies;

	// alternate identities
	vector<string> Ids;

	// booleans for run different variations of design 
	bool runMCAfterSPM; //TRUE: search through sequence space OR FALSE: take best sequences from SPM
	bool runSequenceMC; //TRUE: search for different sequence states OR FALSE: search through rotamer states
	bool runLocalMC; //TRUE: local backbone optimization for each sequence OR FALSE: optimize just the rotamers
	bool useTimeBasedSeed; //TRUE: use time based seed for RandomNumberGenerator OR FALSE: use runNumber as the seed
	bool energyLandscape; //TRUE: collect all sequences and their respective monomer and dimer energies


	// Sequence/State MonteCarlo Options
	int numberEnergyVectors;
	int numStatesToSave;
	double energyLimit;
	double energyDifference;

	// energy terms to output
	vector<string> monomerEnergyTerms;
	vector<string> monomerIMM1EnergyTerms;
	vector<string> dimerEnergyTerms;
	vector<string> calcEnergyOfSequenceTerms;
	vector<string> sequenceMCEnergyTerms;
	vector<string> enerLandscapeTerms;
	vector<string> energyTermsToOutput;
	vector<string> energyTermList;

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

	string configfile;
	string runNumber;
	bool useIMM1;

	//SelfPairManager Options
	bool runDEESingles;
	bool runDEEPairs;
	bool runSCMF;
};

/**************************************************
 *  
 *  =======  PREDECLARATION OF FUNCTIONS =======
 *
 **************************************************/

void usage() {
	cout << endl;
	cout << "Run as" << endl;
	cout << "   % " << programName << " --configfile <file.config>" << endl;
	cout << "For help" << endl;
	cout << "   % " << programName << " -h" << endl;
	cout << endl;
}

void c2Symmetry(AtomPointerVector & _apvA, AtomPointerVector & _apvB) {
	
	/* Faster code 
	for (uint i=0; i < _apvA.size(); i++) {
			_apvB[i]->copyAllCoor(*_apvA[i]);
			vector<CartesianPoint*>& bCoors = _apvB[i]->getAllCoor();

			for(uint j = 0; j < bCoors.size(); j++) {
				bCoors[j]->setX(0 - bCoors[j]->getX());
				bCoors[j]->setY(0 - bCoors[j]->getY());
			}
					
		}
	*/

	// Set coordinates of chain A to chain B
	for (uint i=0; i < _apvA.size(); i++) {
		_apvB[i]->copyAllCoor(*_apvA[i]);
	}

	// Rotation matrix for 180 degrees
	// flips the sign on the x and y coordinates
	Matrix m(3,3,0.0);
	m[0][0] = -1.0;
	m[0][1] = 0.0;
	m[0][2] = 0.0;
	m[1][0] = 0.0;
	m[1][1] = -1.0;
	m[1][2] = 0.0;
	m[2][0] = 0.0;
	m[2][1] = 0.0;
	m[2][2] = 1.0;

	// Rotate chain B around Z axis
	Transforms trans; 
	trans.rotate(_apvB, m);
	
}
//TODO: add these functions to the end of the code and pre-declare them here
// String output functions
string convertToPolymerSequenceNeutralPatch(string _seq, int _startResNum) {
	// convert a 1 letter _sequence like AIGGG and startResNum = 32 to 
	// A:{32}ALA ILE GLY GLY GLY
	// B:{32}ALA ILE GLY GLY GLY
	string ps = "";
	for(string::iterator it = _seq.begin(); it != _seq.end();it++ ) {
		if (it == _seq.begin() || it == _seq.end()-1){
			stringstream ss;
			ss << *it;
			string resName = MslTools::getThreeLetterCode(ss.str());
			if (it == _seq.begin()){
				if(resName == "HIS") {
					ps = ps + " HSE-ACE";
				} else {
					ps = ps + " " + resName + "-ACE";
				}
			}
			else{
				if(resName == "HIS") {
					ps = ps + " HSE-CT2";
				} else {
					ps = ps + " " + resName + "-CT2";
				}
			}
		}
		else{
			stringstream ss;
			ss << *it;
			string resName = MslTools::getThreeLetterCode(ss.str());
			if(resName == "HIS") {
				ps = ps + " HSE";
			} else {
				ps = ps + " " + resName;
			}
		}
	}
	ps = ":{" + MslTools::intToString(_startResNum) + "} " + ps;
	return "A" + ps + "\nB" + ps;
}

string convertToPolymerSequenceNeutralPatchMonomer(string _seq, int _startResNum) {
	// convert a 1 letter _sequence like AIGGG and startResNum = 32 to 
	// A:{32}ALA ILE GLY GLY GLY
	string ps = "";
	for(string::iterator it = _seq.begin(); it != _seq.end();it++ ) {
		if (it == _seq.begin() || it == _seq.end()-1){
			stringstream ss;
			ss << *it;
			string resName = MslTools::getThreeLetterCode(ss.str());
			if (it == _seq.begin()){
				if(resName == "HIS") {
					ps = ps + " HSE-ACE";
				} else {
					ps = ps + " " + resName + "-ACE";
				}
			}
			else{
				if(resName == "HIS") {
					ps = ps + " HSE-CT2";
				} else {
					ps = ps + " " + resName + "-CT2";
				}
			}
		}
		else{
			stringstream ss;
			ss << *it;
			string resName = MslTools::getThreeLetterCode(ss.str());
			if(resName == "HIS") {
				ps = ps + " HSE";
			} else {
				ps = ps + " " + resName;
			}
		}
	}
	ps = ":{" + MslTools::intToString(_startResNum) + "} " + ps;
	return "A" + ps;
}

string convertPolymerSeqToOneLetterSeq(Chain &_chain) {
	string seq = "";
	for (uint i=0; i<_chain.positionSize(); i++){
		string resName = _chain.getPosition(i).getCurrentIdentity().getResidueName();
		string resID = MslTools::getOneLetterCode(resName);
		seq += resID;
	}
	return seq;
}

void addAAIdentities(CharmmSystemBuilder &_CSB, System &_sys, vector<string> _alternateIds, vector<int> _variableInterfacialPositions, int _startResNum, int _seqLength) {
	int counter = 0;
	for(uint i = _startResNum; i<_startResNum+_seqLength; i++) {
		Position &posA = _sys.getChain("A").getPosition(i);
		Position &posB = _sys.getChain("B").getPosition(i);
		if (_variableInterfacialPositions[counter] == 1){
			for (uint j=0; j<_alternateIds.size(); j++){
				_CSB.addIdentity(posA, _alternateIds[j]);
				_CSB.addIdentity(posB, _alternateIds[j]);
			}
		}
		else{
			continue;
		}
		counter++;
	}
}

string generatePolyLeu(string _backboneAA, int _sequenceLength) {
	string polyLeu = "";
	for (uint i=0; i<_sequenceLength; i++){
		polyLeu = polyLeu + _backboneAA;
	}
	return polyLeu;
}

string generateMonomerMultiIDPolymerSequence(string _seq, int _startResNum, vector<string> _alternateIds, vector<int> _variableInterfacialPositions) {
	// convert a 1 letter _sequence like AIGGG and startResNum = 32 to 
	// A:{32}ALA ILE GLY GLY GLY
	string ps = "";
	int counter = 0;
	for(string::iterator it = _seq.begin(); it != _seq.end(); it++) {
		if (it == _seq.begin() || it == _seq.end()-1){
			stringstream ss;
			ss << *it;
			string resName = MslTools::getThreeLetterCode(ss.str());
			if (it == _seq.begin()){
				if(resName == "HIS") {
					ps = ps + " HSE-ACE";
				} else {
					ps = ps + " " + resName + "-ACE";
				}
			}
			else{
				if(resName == "HIS") {
					ps = ps + " HSE-CT2";
				} else {
					ps = ps + " " + resName + "-CT2";
				}
			}
			counter++;
		}
		else{
			stringstream ss;
			ss << *it;
			string resName = MslTools::getThreeLetterCode(ss.str());
			if (_variableInterfacialPositions[counter] == 1){
				ps = ps + " [";
				if(resName == "HIS") {
					ps = ps + " HSE";
				} else {
					ps = ps + " " + resName;
				}
				for (uint i=0; i<_alternateIds.size(); i++){
					if(_alternateIds[i] == "HIS") {
						ps = ps + " HSE";
					} else {
						ps = ps + " " + _alternateIds[i];
					}
				}
				ps = ps + "] ";
			} else {
				if(resName == "HIS") {
					ps = ps + " HSE";
				} else {
					ps = ps + " " + resName;
				}
			}
			counter++;
		}
	}
	ps = ":{" + MslTools::intToString(_startResNum) + "} " + ps;
	return "A" + ps;
}

string generateMultiIDPolymerSequence(string _seq, int _startResNum, vector<string> _alternateIds, vector<int> _variableInterfacialPositions) {
	// convert a 1 letter _sequence like AIGGG and startResNum = 32 to 
	// A:{32}ALA ILE GLY GLY GLY
	// B:{32}ALA ILE GLY GLY GLY
	string ps = "";
	int counter = 0;
	for(string::iterator it = _seq.begin(); it != _seq.end(); it++) {
		if (it == _seq.begin() || it == _seq.end()-1){
			stringstream ss;
			ss << *it;
			string resName = MslTools::getThreeLetterCode(ss.str());
			if (it == _seq.begin()){
				if(resName == "HIS") {
					ps = ps + " HSE-ACE";
				} else {
					ps = ps + " " + resName + "-ACE";
				}
			}
			else{
				if(resName == "HIS") {
					ps = ps + " HSE-CT2";
				} else {
					ps = ps + " " + resName + "-CT2";
				}
			}
			counter++;
		}
		else{
			stringstream ss;
			ss << *it;
			string resName = MslTools::getThreeLetterCode(ss.str());
			if (_variableInterfacialPositions[counter] == 1){
				ps = ps + " [";
				if(resName == "HIS") {
					ps = ps + " HSE";
				} else {
					ps = ps + " " + resName;
				}
				for (uint i=0; i<_alternateIds.size(); i++){
					if(_alternateIds[i] == "HIS") {
						ps = ps + " HSE";
					} else {
						ps = ps + " " + _alternateIds[i];
					}
				}
				ps = ps + "] ";
			} else {
				if(resName == "HIS") {
					ps = ps + " HSE";
				} else {
					ps = ps + " " + resName;
				}
			}
			counter++;
		}
	}
	ps = ":{" + MslTools::intToString(_startResNum) + "} " + ps;
	return "A" + ps + "\nB" + ps;
}

string generatePolymerSequence(string _backboneAA, int _sequenceLength, int _startResNum) {
	string ps = "";
	string resName = MslTools::getThreeLetterCode(_backboneAA);
	if(resName == "HIS") {
		resName = "HSE";
	}
	for (uint i=0; i<_sequenceLength; i++){
		ps = ps + " " + resName;
	}
	ps = ":{" + MslTools::intToString(_startResNum) + "} " + ps;
	return "A" + ps + "\nB" + ps;
}

string generateMonomerPolymerSequenceFromSequence(string _sequence, int _startResNum) {
	string ps = "";
	for (uint i=0; i<_sequence.length(); i++){
		stringstream tmp;
		tmp << _sequence[i];
		string aa = tmp.str();
		string resName = MslTools::getThreeLetterCode(aa);
		if(resName == "HIS") {
			resName = "HSE";
		}
		ps = ps + " " + resName;
	}
	ps = ":{" + MslTools::intToString(_startResNum) + "} " + ps;
	return "A" + ps;
}

string generatePolymerSequenceFromSequence(string _sequence, int _startResNum) {
	string ps = "";
	for (uint i=0; i<_sequence.length(); i++){
		stringstream tmp;
		tmp << _sequence[i];
		string aa = tmp.str();
		string resName = MslTools::getThreeLetterCode(aa);
		if(resName == "HIS") {
			resName = "HSE";
		}
		ps = ps + " " + resName;
	}
	ps = ":{" + MslTools::intToString(_startResNum) + "} " + ps;
	return "A" + ps + "\nB" + ps;
}

void transformation(AtomPointerVector & _chainA, AtomPointerVector & _chainB, AtomPointerVector & _axisA, AtomPointerVector & _axisB, CartesianPoint & _ori, CartesianPoint & _xAxis, CartesianPoint & _zAxis, double _zShift, double _axialRotation, double _crossingAngle, double _xShift, Transforms & _trans) {
	
	//====== Z Shift (Crossing Point) ======
	CartesianPoint zShiftCP(0.0, 0.0, _zShift);
	_trans.translate(_chainA, zShiftCP);

	//===== Axial Rotation ======
	_trans.rotate(_chainA, _axialRotation, _ori, _zAxis);

	//====== Local Crossing Angle ======
	_trans.rotate(_chainA, (_crossingAngle/2.0), _ori, _xAxis);
	_trans.rotate(_axisA, (_crossingAngle/2.0), _ori, _xAxis);

	//====== X shift (Interhelical Distance) =======
	CartesianPoint interDistVect;
	interDistVect.setCoor((-1.0*_xShift/2.0), 0.0, 0.0);
	_trans.translate(_chainA, interDistVect);
	_trans.translate(_axisA, interDistVect);

	c2Symmetry(_chainA, _chainB);
	c2Symmetry(_axisA, _axisB);
}

vector<vector<vector<vector<bool>>>> createSavedEnergyFlagTable(System & _sys) {
	vector<vector<vector<vector<bool> > > > savedEnergyFlagTable; // true if the energy is computed already and available
	vector<unsigned int> variablePos = _sys.getVariablePositions();

	for (int i=0; i<variablePos.size(); i++) {
		savedEnergyFlagTable.push_back(vector<vector<vector<bool> > >());
		//cout << i;

		for (int j=0; j < _sys.getPosition(variablePos[i]).getTotalNumberOfRotamers(); j++) {
			savedEnergyFlagTable[i].push_back(vector<vector<bool> >());
			//cout << " " << i << "/" << j << "-";

			for (int k=0; k < i; k++) {
				if (i==k) {
					continue;
				}
				savedEnergyFlagTable[i][j].push_back(vector<bool>());

				for (int l=0; l < _sys.getPosition(variablePos[k]).getTotalNumberOfRotamers(); l++) {
			//		cout << " " << k << "/" << l;
					if (_sys.getPosition(variablePos[i]).getChainId() == _sys.getPosition(variablePos[k]).getChainId()) {
						savedEnergyFlagTable[i][j][k].push_back(true);
			//			cout << "=T";
					}
					else {
						savedEnergyFlagTable[i][j][k].push_back(false);
			//			cout << "=F";
					}
				}
			}
		}
		//cout << endl;
	}

	return savedEnergyFlagTable;
}

void repackSideChains(SelfPairManager & _spm, int _greedyCycles) {
	_spm.setOnTheFly(1);
	_spm.calculateEnergies(); // CHANGE BACK!!!
	_spm.runGreedyOptimizer(_greedyCycles);
}

void repackSideChains(SelfPairManager & _spm, int _greedyCycles, vector<vector<vector<vector<bool> > > > _savedEnergyFlagTable) {
	_spm.setOnTheFly(1);
	_spm.recalculateNonSavedEnergies(_savedEnergyFlagTable);
	_spm.runGreedyOptimizer(_greedyCycles);
}

void readGeometryFile(string _filename, vector<string>& _fileVec) {
	ifstream file;
	file.open(_filename.c_str()); 
	if(!file.is_open()) {
		cerr << "Unable to open " << _filename << endl;
		exit(0);
	}

	string parameterList;

	while(file) {
		getline(file, parameterList);
		_fileVec.push_back(parameterList);
	}
	file.close();
}

void moveZCenterOfCAMassToOrigin(AtomPointerVector& _apV, AtomPointerVector& _axis, Transforms & _trans) {

	AtomSelection sel(_apV);
	AtomPointerVector & caApV = sel.select("name CA");
	double zShift = 0.0;
	for(int i = 0; i < caApV.size(); i++) {
		zShift += (caApV[i]->getCoor()).getZ();
	}
	zShift = -1.0 * zShift/double(caApV.size());
	//fout << x << " " << y << " " << pt << " " << caApV.size() << endl;

	// old code
	//for(int i = 0; i < _apV.size(); i++) {
	//	CartesianPoint& pt = _apV[i]->getCoor();
	//	pt.setZ(pt.getZ() +  zShift);
	//}

	CartesianPoint interDistVect;
	interDistVect.setCoor(0.0, 0.0, zShift);
	_trans.translate(_apV, interDistVect);
	_trans.translate(_axis, interDistVect);
	

}

void deleteTerminalHydrogenBondInteractions(System &_sys, Options &_opt){
	EnergySet* pESet = _sys.getEnergySet();
	int chainSize = _sys.chainSize();
	int frontExt = _opt.tmStart;
	int endExt = _opt.endResNum;
	AtomPointerVector atoms;
	for(int i = 0; i < chainSize; i++) {
		Chain & thisChain = _sys.getChain(i);
		vector<Position*>& positions = thisChain.getPositions();
		for(int i = 0; i < 3; i++) {
			if(frontExt > i) {
				atoms += positions[i]->getAtomPointers();
			}
			if(endExt > i) {
				atoms += positions[positions.size() - 1 - i]->getAtomPointers();
			}
		}
	}
	pESet->deleteInteractionsWithAtoms(atoms,"SCWRL4_HBOND");
}

Options parseOptions(int _argc, char * _argv[], Options defaults);

void printOptions(Options & _op, ofstream & _fout) {
	_fout << "Program " << programName << " v." << programVersion << ", " << programDate << ", (MSL v." << mslVersion << " " << mslDate << ")" << endl;

	_fout << "Warning Messages: " << _op.warningMessages << endl << endl;

	_fout << "Other Parameters" << endl;
	_fout << "backboneCrd " << _op.backboneCrd << endl;
	//_fout << "logFile " << _op.logFile << endl;
	_fout << "pdbOutputDir " << _op.pdbOutputDir << endl;

	//_fout << "fullSequence " << _op.fullSequence << endl;
	_fout << "tmStart " << _op.tmStart << endl;
	_fout << "tmEnd " << _op.tmEnd << endl;

	_fout << "topFile " << _op.topFile << endl;
	_fout << "parFile " << _op.parFile << endl;
	_fout << "baselineFile " << _op.baselineFile << endl;
	_fout << "solvFile " << _op.solvFile << endl;
	_fout << "hBondFile " << _op.hBondFile << endl;
	_fout << "rotLibFile " << _op.rotLibFile << endl;
	_fout << "monoRotLibFile " << _op.monoRotLibFile << endl;

	_fout << "MCCycles " << _op.MCCycles << endl;
	_fout << "MCMaxRejects " << _op.MCMaxRejects << endl;
	_fout << "MCStartTemp " << _op.MCStartTemp << endl;
	_fout << "MCEndTemp " << _op.MCEndTemp << endl;
	_fout << "MCCurve " << _op.MCCurve << endl;

	_fout << "deltaZ " << _op.deltaZ << endl;
	_fout << "deltaAx " << _op.deltaAx << endl;
	_fout << "deltaCross " << _op.deltaCross << endl;
	_fout << "deltaX " << _op.deltaX << endl;

	_fout << "verbose " << _op.verbose << endl;
	_fout << "greedyCycles " << _op.greedyCycles << endl;
	_fout << "seed " << _op.seed << endl;

	_fout << "numberOfStructuresToMCRepack " << _op.numberOfStructuresToMCRepack << endl;
	_fout << "energyCutOff " << _op.energyCutOff << endl;

	_fout << "monoE_vdw " << _op.monoE_vdw << endl;
	_fout << "monoE_solv " << _op.monoE_solv << endl;
	_fout << "monoE_solvRef" << _op.monoE_solvRef << endl;
	_fout << "monoE_hbond" << _op.monoE_hbond << endl;

	_fout << "printAllCrds " << _op.printAllCrds << endl;
	_fout << "printAxes " << _op.printAxes << endl;
	_fout << "printTermEnergies " << _op.printTermEnergies << endl;
	_fout << "deleteTerminalHbonds " << _op.deleteTerminalHbonds << endl;

	_fout << "fullSequenceStart " << _op.sequenceStart << endl;

	_fout << "startResNum " << _op.startResNum << endl;
	_fout << "endResNum " << _op.endResNum << endl;

	_fout << "thread " << _op.thread << endl;

	_fout << "weight_vdw " << _op.weight_vdw << endl;
	_fout << "weight_hbond " << _op.weight_hbond << endl;
	_fout << "weight_solv " << _op.weight_solv << endl;
	_fout << "weight_seqEntropy " << _op.weight_seqEntropy << endl;

	if(_op.configfile != "") {
		_fout << "configfile " << _op.configfile << endl;
	}

	_fout << endl;

}

void loadMonomerRotamers(System &_sys, SystemRotamerLoader &_sysRot){
	for (uint k=0; k<_sys.positionSize(); k++) {
		Position &pos = _sys.getPosition(k);
		if (pos.getResidueName() != "GLY" && pos.getResidueName() != "ALA" && pos.getResidueName() != "PRO") {
			if (!_sysRot.loadRotamers(&pos, pos.getResidueName(), "SL90.00")) {//lower rotamer level because I did baselines at this level
				cerr << "Cannot load rotamers for " << pos.getResidueName() << endl;
			}
		}
	}	
}

void loadRotamers(System &_sys, SystemRotamerLoader &_sysRot, string _SL){
	for (uint k=0; k<_sys.positionSize(); k++) {
		Position &pos = _sys.getPosition(k);
		if (pos.identitySize() > 1){
			for (uint j=0; j < pos.getNumberOfIdentities(); j++){
				pos.setActiveIdentity(j);
				if (pos.getResidueName() != "GLY" && pos.getResidueName() != "ALA" && pos.getResidueName() != "PRO") {
					if (!_sysRot.loadRotamers(&pos, pos.getResidueName(), _SL)) {
						cerr << "Cannot load rotamers for " << pos.getResidueName() << endl;
					}
				}
				pos.setActiveIdentity(0);
			}
		}
		else{
			if (pos.getResidueName() != "GLY" && pos.getResidueName() != "ALA" && pos.getResidueName() != "PRO") {
				if (!_sysRot.loadRotamers(&pos, pos.getResidueName(), _SL)) {
					cerr << "Cannot load rotamers for " << pos.getResidueName() << endl;
				}
			}
		}
	}	
}

void loadRotamersCurrId(System &_sys, SystemRotamerLoader &_sysRot, string _SL){
	for (uint k=0; k<_sys.positionSize(); k++) {
		Position &pos = _sys.getPosition(k);
		if (pos.getResidueName() != "GLY" && pos.getResidueName() != "ALA" && pos.getResidueName() != "PRO") {
			if (!_sysRot.loadRotamers(&pos, pos.getResidueName(), _SL)) {
				cerr << "Cannot load rotamers for " << pos.getResidueName() << endl;
			}
		}
		else{
			if (pos.getResidueName() != "GLY" && pos.getResidueName() != "ALA" && pos.getResidueName() != "PRO") {
				if (!_sysRot.loadRotamers(&pos, pos.getResidueName(), _SL)) {
					cerr << "Cannot load rotamers for " << pos.getResidueName() << endl;
				}
			}
		}
	}	
}

//below function only loads rotamers onto the interfacial positions by variableInterfacialPositions (01 where 0 = non-interfacial and 1 = interfacial)
void loadInterfacialRotamers(System &_sys, SystemRotamerLoader &_sysRot, string _SL, vector<int> _interface){
	for (uint k=0; k<_interface.size(); k++) {
		if (_interface[k] == 1){
			Position &pos = _sys.getPosition(k);
			if (pos.identitySize() > 1){
				for (uint j=0; j < pos.getNumberOfIdentities(); j++){
					pos.setActiveIdentity(j);
					if (pos.getResidueName() != "GLY" && pos.getResidueName() != "ALA" && pos.getResidueName() != "PRO") {
						if (!_sysRot.loadRotamers(&pos, pos.getResidueName(), _SL)) {
							cerr << "Cannot load rotamers for " << pos.getResidueName() << endl;
						}
					}
					pos.setActiveIdentity(0);
				}
			}
			else{
				if (pos.getResidueName() != "GLY" && pos.getResidueName() != "ALA" && pos.getResidueName() != "PRO") {
					if (!_sysRot.loadRotamers(&pos, pos.getResidueName(), _SL)) {
						cerr << "Cannot load rotamers for " << pos.getResidueName() << endl;
					}
				}
			}
		}	
	}
}

void loadInterfacialPeripheralRotamers(System &_sys, SystemRotamerLoader &_sysRot, string _SL, vector<int> _interface){
	for (uint k=0; k<_interface.size(); k++) {
		if (_interface[k] == 1){
			Position &posA = _sys.getPosition(k-1);
			Position &posB = _sys.getPosition(k+1);
			if (posA.identitySize() > 1){
				for (uint j=0; j < posA.getNumberOfIdentities(); j++){
					posA.setActiveIdentity(j);
					if (posA.getResidueName() != "GLY" && posA.getResidueName() != "ALA" && posA.getResidueName() != "PRO") {
						if (!_sysRot.loadRotamers(&posA, posA.getResidueName(), _SL)) {
							cerr << "Cannot load rotamers for " << posA.getResidueName() << endl;
						}
					}
					posA.setActiveIdentity(0);
				}
			}
			else{
				if (posA.getResidueName() != "GLY" && posA.getResidueName() != "ALA" && posA.getResidueName() != "PRO") {
					if (!_sysRot.loadRotamers(&posA, posA.getResidueName(), _SL)) {
						cerr << "Cannot load rotamers for " << posA.getResidueName() << endl;
					}
				}
			}
			if (posB.identitySize() > 1){
				for (uint j=0; j < posB.getNumberOfIdentities(); j++){
					posB.setActiveIdentity(j);
					if (posB.getResidueName() != "GLY" && posB.getResidueName() != "ALA" && posB.getResidueName() != "PRO") {
						if (!_sysRot.loadRotamers(&posB, posB.getResidueName(), _SL)) {
							cerr << "Cannot load rotamers for " << posB.getResidueName() << endl;
						}
					}
					posB.setActiveIdentity(0);
				}
			}
			else{
				if (posB.getResidueName() != "GLY" && posB.getResidueName() != "ALA" && posB.getResidueName() != "PRO") {
					if (!_sysRot.loadRotamers(&posB, posB.getResidueName(), _SL)) {
						cerr << "Cannot load rotamers for " << posB.getResidueName() << endl;
					}
				}
			}
		}	
	}
}

//Interface identified using occluded surface area
void identifyInterface(System &_sys, Options &_opt, PolymerSequence _PS, vector<int> &_pos, ofstream &_out, string _axis){
	// Declare system
	System sys;
	CharmmSystemBuilder CSB(sys,_opt.topFile,_opt.parFile);
	CSB.setBuildNoTerms();
	
	if(!CSB.buildSystem(_PS)) {
		cout << "Unable to build system from " << _PS << endl;
		exit(0);
	} else {
		//fout << "CharmmSystem built for sequence" << endl;
	}

	Chain & chainA = sys.getChain("A");
	Chain & chainB = sys.getChain("B");

	sys.assignCoordinates(_sys.getAtomPointers(), false);

	// Set up chain A and chain B atom pointer vectors
	AtomPointerVector & apvChainA = chainA.getAtomPointers();
	AtomPointerVector & apvChainB = chainB.getAtomPointers();

	PDBReader readAxis;
	if(!readAxis.read(_axis)) {
		cout << "Unable to read axis" << endl;
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

	// Objects used for transformations
	Transforms trans; 
	trans.setTransformAllCoors(true); // transform all coordinates (non-active rotamers)
	trans.setNaturalMovements(true); // all atoms are rotated such as the total movement of the atoms is minimized

	// Transformation to zShift, axialRotation, crossingAngle, and xShift
	transformation(apvChainA, apvChainB, axisA, axisB, ori, xAxis, zAxis, _opt.zShift, _opt.axialRotation, _opt.crossingAngle, 6.4, trans);//one of the shortest distances given from my pdb searc
	moveZCenterOfCAMassToOrigin(sys.getAtomPointers(), helicalAxis.getAtomPointers(), trans);
	
	sys.buildAllAtoms();

	// Setup output files
	//ofstream out;
	//string outfile  = _outputDir + "/Interface_SASA.out";
	//out.open(outfile.c_str());
	_out << "Using SASA values, interfacial residues are chosen for any SASA with less than the average SASA" << endl << endl;
	
	//PDBWriter writer;
	//writer.open(_outputDir + "/polyAla_for_SASA.pdb");
	//writer.write(sys.getAtomPointers(),true,false,true);
	//writer.close();

	// Setup SASA calculator
	SasaCalculator sa;
	sa.addAtoms(sys.getAtomPointers());

	sa.calcSasa();
	double totSasa = 0;
	double worstSasa = 0;
	vector<double> sasas;
	vector<int> pos;
	vector<string> posIds;

	// Get all SASA values for each residue on one chain of internal positions
	_out << "SASA values per residue:" << endl;
	for (uint k=1; k<sys.getChain("A").positionSize()-1; k++) {
		Position &pos1 = sys.getChain("A").getPosition(k);
		
		Atom &c1 = pos1.getAtom("CA");
		string posId = c1.getPositionId();

		// Get SASA value for each residue and add to SASA vector
		double sasa = sa.getResidueSasa(posId);
		_out << posId << ": " << sasa << endl;
		//cout << posId << ": " << sasa << endl;
		totSasa = totSasa+sasa;
		sasas.push_back(sasa);
		pos.push_back(k);
		posIds.push_back(posId);
		if (k == 4){
			worstSasa = sasa;
		}
		else if (k < sys.getChain("A").positionSize()-4){
			if (sasa > worstSasa){
				worstSasa = sasa;
			}
		}
	}
	_out << "Total SASA: " << totSasa << endl;
	_out << "Avg SASA: " << totSasa/19 << endl;

	// Get the interface by values less average of internal SASA positions 
	double cutoff = totSasa/19;
	//TODO: add in another cutoff for peripheral AAs so that back are just fixed
	_out << "Residues chosen with less than " << cutoff << " SASA:" << endl;
	for (uint j=0;j<sasas.size(); j++){
		if (sasas[j] < cutoff){
			_pos.push_back(pos[j]);
			_out << posIds[j] << endl;
		}
	}
}

//boolean added to make multiple interface01 (I need to keep Leu in the first 4AAs because of baseline, but some are considered interfacial and should have more rotamers)
vector<int> interface01(System &_sys, vector<int> &_pos, bool _onlyInterface=true){
	vector<int> variableInterfacialPositions;
	for (uint k=0; k<_sys.positionSize(); k++){
		variableInterfacialPositions.push_back(0);
	}
	for (uint j=0; j<_pos.size(); j++){
		variableInterfacialPositions[_pos[j]] = 1;
		variableInterfacialPositions[_pos[j]+_sys.getChain("A").positionSize()] = 1;
	}
	if (_onlyInterface == false){
		for (uint k=0; k<4; k++){
			variableInterfacialPositions[k] = 0;
			variableInterfacialPositions[k+_sys.getChain("A").positionSize()] = 0;
		}
		for (uint k=_sys.getChain("A").positionSize()-4; k<_sys.getChain("A").positionSize(); k++){
			variableInterfacialPositions[k] = 0;
			variableInterfacialPositions[k+_sys.getChain("A").positionSize()] = 0;
		}
	}
	return variableInterfacialPositions;
}

//Convert positions to string for setLinkedPositions(std::vector<std::vector<std::string> > &_linkedPositions) which uses "A,19" "B,19" format!
vector<vector<string>> positionToString(System &_sys, vector<int> &_variableInterfacialPositions){
	vector<vector<string>> stringPositions;
	if (_variableInterfacialPositions.size()%2){
		for (uint k=0; k<_variableInterfacialPositions.size()/2; k++){
			//lout << "string" << endl;
			if (_variableInterfacialPositions[k] == 1){
				vector<string> tempPos;
	
				Position &posA = _sys.getPosition(k);
				Position &posB = _sys.getPosition(k+_variableInterfacialPositions.size()/2);
	
				string A = posA.toString();
				string B = posB.toString();
	
				string delimiter = " ";
				
				size_t p = 0;
				p = A.find(delimiter);
	
				tempPos.push_back(A.substr(0, p));
				tempPos.push_back(B.substr(0, p));
	
				stringPositions.push_back(tempPos);
			}
			else{
				continue;
			}
		}
	}
	else{
		for (uint k=0; k<_variableInterfacialPositions.size()/2+1; k++){
			//lout << "string" << endl;
			if (_variableInterfacialPositions[k] == 1){
				vector<string> tempPos;
	
				Position &posA = _sys.getPosition(k);
				Position &posB = _sys.getPosition(k+_variableInterfacialPositions.size()/2);
	
				string A = posA.toString();
				string B = posB.toString();
	
				string delimiter = " ";
				
				size_t p = 0;
				p = A.find(delimiter);
	
				tempPos.push_back(A.substr(0, p));
				tempPos.push_back(B.substr(0, p));
	
				stringPositions.push_back(tempPos);
			}
			else{
				continue;
			}
		}

	}
	return stringPositions;
}

//Identify which positions are found at the identified interface (example: Sequence LLLLIGLLIGLLIGLLLL would be 000011001100110000 where positions at interface are 1, others are 0)
vector<int> getVariablePos(vector<int> &_variableInterfacialPositions){
	vector<int> pos;
	if (_variableInterfacialPositions.size()%2){
		for (int k=0; k<_variableInterfacialPositions.size()/2; k++){
			if (_variableInterfacialPositions[k] == 1){
				pos.push_back(k);
			}
			else{
				continue;
			}
		}
	}
	else{
		for (int k=0; k<_variableInterfacialPositions.size()/2+1; k++){
			if (_variableInterfacialPositions[k] == 1){
				pos.push_back(k);
			}
			else{
				continue;
			}
		}

	}
	return pos;
}

map<string,double> getEnergyByTermDoubled(EnergySet* _eSet) {
	// get all terms
	map<string,double> eByTerm;
	map<string,vector<Interaction*> > * allTerms = _eSet->getEnergyTerms();
	for(map<string,vector<Interaction*> >::iterator it = allTerms->begin(); it != allTerms->end(); it++) {
		if(_eSet->isTermActive(it->first)) {
			eByTerm[it->first] =  2.0* _eSet->getTermEnergy(it->first);
		}
	}
	return eByTerm;
}

double getStandardNormal(RandomNumberGenerator& RNG) {
	double retVal = 0.0;
	for(int i = 0; i < 10; i ++) {
		retVal += RNG.getRandomDouble();
	}
	return (retVal/10.0 - 0.5) * 1.2;
}

string getInterfaceString(vector<int> _interface, int _seqLength){
	string interfaceString = "";
	for (uint i=0; i<_interface.size(); i++){
		if (i == _seqLength){
			i = _interface.size();
		}
		else{
			interfaceString += MslTools::intToString(_interface[i]);
		}
	}
	return interfaceString;
}

string getAlternateIdString(vector<string> _alternateIds){ 
	string alternateIdsString = "";
	for (uint i=0; i<_alternateIds.size(); i++){
		if (i == _alternateIds.size()-1){
			alternateIdsString += _alternateIds[i];
		}
		else{
			alternateIdsString += _alternateIds[i] += " ";
		}
	}
	return alternateIdsString;
}

//Function to calculate the self energies of a chain
vector<double> calcBaselineEnergies(System &_sys, int _seqLength){
	vector<double> ener;
	AtomSelection sel(_sys.getAtomPointers());
	for (uint i=0; i<_seqLength; i++){
		string residue = "resi, chain A and resi ";
		string number = to_string(i+1);
		sel.select(residue += number);
		double resi = _sys.calcEnergy("resi");
		ener.push_back(resi);
	}
	sel.clearStoredSelections();
	return ener;
}

//Function to calculate the pair energies of a chain
vector<double> calcPairBaselineEnergies(System &_sys, int _seqLength){
	vector<double> ener;
	AtomSelection sel(_sys.getAtomPointers());

	for (uint i=0; i<_seqLength; i++){
		string residue = "resi1, chain A and resi ";
		string num1 = to_string(i+1);
		sel.select(residue += num1);
		for (uint j=i+1; j<_seqLength;j++){
			int dist = j-i;
			if (dist <= 10){
				string resi1 = "resi2, chain A and resi ";
				string num2 = to_string(j+1);
				sel.select(resi1 += num2);
				double pair = _sys.calcEnergy("resi1", "resi2");
				ener.push_back(pair);
			}
			else{
				j = _seqLength;
			}
		}
	}
	sel.clearStoredSelections();
	return ener;
}

//Function to get the sum of a vector of doubles, typically energies
double sumEnergyVector(vector<double> _energies){
	double ener = 0;
	for (uint i=0; i<_energies.size(); i++){
		ener = ener + _energies[i];
	}
	return ener;
}

//TODO: add in a way to tell specifically where the error is occurring (monomer, dimer, etc.)
void checkIfAtomsAreBuilt(System &_sys, ofstream &_err){
	for (uint i=0; i<_sys.atomSize(); i++){
		Atom atom = _sys.getAtom(i);
		if (!atom.hasCoor()){
			_err << "Atom " << i << " was not assigned coordinates; program termination";
			cout << "Atom " << i << " was not assigned coordinates; program termination";
			break;
		}
		else{
			continue;
		}
	}
}

//Compute the monomer energy without making movements within the membrane
double computeMonomerEnergyNoMoves(System & _sys, Options &_opt, SelfPairManager &_monoSpm, vector<vector<vector<vector<bool>>>> _savedEnergyFlagTable, map<string,double> &_seqMCEnergies, string &_seq, RandomNumberGenerator &_RNG, int _greedyCycles, int _MCCycles, int _MCMaxRejects, ofstream &_err) {
	map<string,map<string,double>> monomerEnergies;
	string polySeq = convertToPolymerSequenceNeutralPatchMonomer(_seq, 1);//03_26_21: found my monomer issue (maybe?); In the baselineSelfPairComparison code, this had to be 1 to line up with the baselines
	PolymerSequence PS(polySeq);

	// Declare new system
	System monoSys;
	CharmmSystemBuilder CSBMono(monoSys, _opt.topFile, _opt.parFile);
	CSBMono.setBuildTerm("CHARMM_ELEC", false);
	CSBMono.setBuildTerm("CHARMM_ANGL", false);
	CSBMono.setBuildTerm("CHARMM_BOND", false);
	CSBMono.setBuildTerm("CHARMM_DIHE", false);
	CSBMono.setBuildTerm("CHARMM_IMPR", false);
	CSBMono.setBuildTerm("CHARMM_U-BR", false);

	CSBMono.setBuildNonBondedInteractions(false);
	if (!CSBMono.buildSystem(PS)){
		cerr << "Unable to build system from " << polySeq << endl;
	}

	/******************************************************************************
	 *                         === INITIALIZE POLYGLY ===
	 ******************************************************************************/
	// Read in Gly-69 to use as backbone coordinate template
	CRDReader cRead;
	cRead.open(_opt.backboneCrd); 
	if(!cRead.read()) {
		cerr << "Unable to read " << _opt.backboneCrd << endl;
		exit(0);
	}
	cRead.close();

	AtomPointerVector& glyAPV = cRead.getAtomPointers();//*/

	/******************************************************************************
	 *                         === INITIALIZE POLYGLY ===
	 ******************************************************************************/
	monoSys.assignCoordinates(glyAPV,false);
	monoSys.buildAllAtoms();

	CSBMono.updateNonBonded(10,12,50);

	SystemRotamerLoader monoRot(monoSys, _opt.rotLibFile);
	monoRot.defineRotamerSamplingLevels();

	// Add hydrogen bond term
	HydrogenBondBuilder monohb(monoSys, _opt.hBondFile);
	monohb.buildInteractions(50);

	/******************************************************************************
	 *                === CHECK TO SEE IF ALL ATOMS ARE BUILT ===
	 ******************************************************************************/
	checkIfAtomsAreBuilt(monoSys, _err);

	/******************************************************************************
	 *                     === INITIAL VARIABLE SET UP ===
	 ******************************************************************************/
	EnergySet* monoEset = monoSys.getEnergySet();
	monoEset->setAllTermsActive();
	monoEset->setTermActive("CHARMM_ELEC", false);
	monoEset->setTermActive("CHARMM_ANGL", false);
	monoEset->setTermActive("CHARMM_BOND", false);
	monoEset->setTermActive("CHARMM_DIHE", false);
	monoEset->setTermActive("CHARMM_IMPR", false);
	monoEset->setTermActive("CHARMM_U-BR", false);

	monoEset->setWeight("CHARMM_VDW", _opt.weight_vdw);
	monoEset->setWeight("SCWRL4_HBOND", 1);

	//BaselineAAComposition bac(&monoSys);
	//bac.readPenaltyFile("/exports/home/gloiseau/mslib/trunk_AS/myProgs/gloiseau/AACompositionPenalties.out");
	//monoEset->addInteraction(new BaselineAAComposition(bac));
	
	/*****************************************************************************
	 *              === DELETE TERMINAL HYDROGEN BOND INTERACTIONS ===
	 ******************************************************************************/
	deleteTerminalHydrogenBondInteractions(monoSys,_opt);
	
	/*****************************************************************************
	 *                 === GREEDY TO OPTIMIZE ROTAMERS ===
	 ******************************************************************************/
	//loadRotamers(monoSys, monoRot, _opt.SL);
	loadMonomerRotamers(monoSys, monoRot);

	// Optimize Initial Starting Position (using Baseline to get back to original result)
	_monoSpm.setSystem(&monoSys);

	repackSideChains(_monoSpm, _opt.greedyCycles);
	//repackSideChains(_monoSpm, _opt.greedyCycles, _savedEnergyFlagTable);

	/*****************************************************************************
	 *            === SET SYSTEM TO BEST SPM ROTAMERS AND OUTPUT ===
	 ******************************************************************************/
	//_monomerMinState.push_back(_monoSpm.getMinStates()[0]);
	monoSys.setActiveRotamers(_monoSpm.getMinStates()[0]);
	monoSys.calcEnergy();
	
	string monoOutPdbFile  = _opt.pdbOutputDir + "/monomer.pdb";
	PDBWriter monoPdb;
	monoPdb.setConvertFormat("CHARMM22","PDB2");
	monoPdb.open(monoOutPdbFile);
	if(!monoPdb.write(monoSys.getAtomPointers())) {
		cerr << "Unable to write " << monoOutPdbFile << endl;
		exit(0);
	}

	double monomerEnergy = 2.0 * _monoSpm.getMinBound()[0]; // double the energy for 2 helices
	vector<double> self = calcBaselineEnergies(monoSys, _opt.backboneLength);
	vector<double> pair = calcPairBaselineEnergies(monoSys, _opt.backboneLength);
	double monomerSelf = sumEnergyVector(self)*2.0;
	double monomerPair = sumEnergyVector(pair)*2.0;

	for (uint i=0; i<_opt.energyTermList.size(); i++){
		string energyTerm = _opt.energyTermList[i];
		string energyLabel = energyTerm.substr(7,energyTerm.length())+"MonomerNoIMM1";
		_seqMCEnergies[energyLabel] = monoEset->getTermEnergy(_opt.energyTermList[i])*2;
	}
	_seqMCEnergies["MonomerSelfBaseline"] = monomerSelf;
	_seqMCEnergies["MonomerPairBaseline"] = monomerPair;
	_seqMCEnergies["MonomerNoIMM1"] = monomerEnergy;

	monoPdb.close();
	return monomerEnergy;
}

//TODO: make this easier to understand
void outputEnergiesByTerm(SelfPairManager &_spm, vector<uint> _stateVec, map<string,double> &_energyMap, vector<string> _energyTermList, string _energyDescriptor, double _type){
	if (_type == 0){//No IMM1 Energy (for the Monte Carlos, both dimer and monomer)
		for (uint i=0; i<_energyTermList.size(); i++){
			string energyTerm = _energyTermList[i]; //CHARMM_ and SCWRL4_ terms
			string energyLabel = energyTerm.substr(7,energyTerm.length())+_energyDescriptor;//Removes the CHARMM_ and SCWRL4_ before energyTerm names
			if (energyTerm.find("IMM1") != string::npos){
				//skip these terms (not calculated in the stateMC)
				continue;
			}
			else{
				if (_energyDescriptor.find("Monomer") != string::npos){
					_energyMap[energyLabel] = _spm.getStateEnergy(_stateVec, energyTerm)*2;
				}
				else{
					_energyMap[energyLabel] = _spm.getStateEnergy(_stateVec, energyTerm);
				}
			}
		}
		if (_energyDescriptor.find("Monomer") != string::npos){
			//skip if monomer; could add calc baseline here at some point
		}
		else{
			_energyMap["Baseline"] = _spm.getStateEnergy(_stateVec,"BASELINE")+_spm.getStateEnergy(_stateVec,"BASELINE_PAIR");
			_energyMap["DimerSelfBaseline"] = _spm.getStateEnergy(_stateVec,"BASELINE");
			_energyMap["DimerPairBaseline"] = _spm.getStateEnergy(_stateVec,"BASELINE_PAIR");
			double nonBaselineEnergy = _spm.getStateEnergy(_stateVec,"CHARMM_VDW")+_spm.getStateEnergy(_stateVec,"SCWRL4_HBOND");
		}
	}
	else if (_type == 1){//IMM1 Energies
		for (uint i=0; i<_energyTermList.size(); i++){
			string energyTerm = _energyTermList[i];
			string energyLabel = energyTerm.substr(7,energyTerm.length())+_energyDescriptor;
			if (_energyDescriptor.find("Monomer") != string::npos){
				if (energyTerm.find("IMM1") != string::npos){
					_energyMap["IMM1Monomer"] = (_spm.getStateEnergy(_stateVec,"CHARMM_IMM1")+_spm.getStateEnergy(_stateVec,"CHARMM_IMM1REF"))*2;
				}
				else{
					_energyMap[energyLabel] = _spm.getStateEnergy(_stateVec, energyTerm)*2;
				}
			}
			else{
				if (energyTerm.find("IMM1") != string::npos){
					_energyMap["IMM1Dimer"] = _spm.getStateEnergy(_stateVec,"CHARMM_IMM1")+_spm.getStateEnergy(_stateVec,"CHARMM_IMM1REF");
				}
				else{
					_energyMap[energyLabel] = _spm.getStateEnergy(_stateVec, energyTerm);
				}
			}
		}
	}
}

//Compute monomer energy with movements within the membrane
double computeMonomerEnergy(System & _sys, Options& _opt, Transforms & _trans, int _seqNumber, map<string,map<string,double>> &_seqEnergyMap, string _seq, RandomNumberGenerator &_RNG, int _greedyCycles, int _MCCycles, int _MCMaxRejects, ofstream &_err) {

	//string polySeq = convertToPolymerSequenceNeutralPatchMonomer(_seq, _opt.thread);//fixed monomer calculation issue on 05_12_2021
	string polySeq = generateMonomerPolymerSequenceFromSequence(_seq, _opt.thread);
	PolymerSequence PS(polySeq);

	// Declare new system
	System monoSys;
	CharmmSystemBuilder CSBMono(monoSys, _opt.topFile, _opt.parFile, _opt.solvFile);
	CSBMono.setBuildTerm("CHARMM_ELEC", false);
	CSBMono.setBuildTerm("CHARMM_ANGL", false);
	CSBMono.setBuildTerm("CHARMM_BOND", false);
	CSBMono.setBuildTerm("CHARMM_DIHE", false);
	CSBMono.setBuildTerm("CHARMM_IMPR", false);
	CSBMono.setBuildTerm("CHARMM_U-BR", false);
	CSBMono.setBuildTerm("CHARMM_IMM1REF", true);
	CSBMono.setBuildTerm("CHARMM_IMM1", true);

	CSBMono.setSolvent("MEMBRANE");
	CSBMono.setIMM1Params(15, 10);

	CSBMono.setBuildNonBondedInteractions(false);
	if (!CSBMono.buildSystem(PS)){
		cerr << "Unable to build system from " << polySeq << endl;
	}

	/******************************************************************************
	 *                         === INITIALIZE POLYGLY ===
	 ******************************************************************************/
	// Read in Gly-69 to use as backbone coordinate template
	CRDReader cRead;
	cRead.open(_opt.backboneCrd); 
	if(!cRead.read()) {
		cerr << "Unable to read " << _opt.backboneCrd << endl;
		exit(0);
	}
	cRead.close();

	AtomPointerVector& glyAPV = cRead.getAtomPointers();//*/

	/******************************************************************************
	 *                         === INITIALIZE POLYGLY ===
	 ******************************************************************************/
	monoSys.assignCoordinates(glyAPV,false);
	monoSys.buildAllAtoms();

	CSBMono.updateNonBonded(10,12,50);

	SystemRotamerLoader monoRot(monoSys, _opt.rotLibFile);
	monoRot.defineRotamerSamplingLevels();

	// Add hydrogen bond term
	HydrogenBondBuilder monohb(monoSys, _opt.hBondFile);
	monohb.buildInteractions(50);

	/******************************************************************************
	 *                === CHECK TO SEE IF ALL ATOMS ARE BUILT ===
	 ******************************************************************************/
	checkIfAtomsAreBuilt(monoSys, _err);
	
	/*****************************************************************************
	 *              === DELETE TERMINAL HYDROGEN BOND INTERACTIONS ===
	 ******************************************************************************/
	deleteTerminalHydrogenBondInteractions(monoSys,_opt);
	
	/******************************************************************************
	 *                     === INITIAL VARIABLE SET UP ===
	 ******************************************************************************/
	EnergySet* monoEset = monoSys.getEnergySet();
	monoEset->setAllTermsActive();
	monoEset->setTermActive("CHARMM_ELEC", false);
	monoEset->setTermActive("CHARMM_ANGL", false);
	monoEset->setTermActive("CHARMM_BOND", false);
	monoEset->setTermActive("CHARMM_DIHE", false);
	monoEset->setTermActive("CHARMM_IMPR", false);
	monoEset->setTermActive("CHARMM_U-BR", false);
	monoEset->setTermActive("CHARMM_IMM1REF", true);
	monoEset->setTermActive("CHARMM_IMM1", true);
	monoEset->setTermActive("CHARMM_VDW", true);
	monoEset->setTermActive("SCWRL4_HBOND", true);

	monoEset->setWeight("CHARMM_VDW", 1);
	monoEset->setWeight("SCWRL4_HBOND", 1);
	monoEset->setWeight("CHARMM_IMM1REF", 1);
	monoEset->setWeight("CHARMM_IMM1", 1);
	
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
		cout << "Unable to read axis" << endl;
		exit(0);
	}

	System helicalAxis;
	helicalAxis.addAtoms(readAxis.getAtomPointers());

	AtomPointerVector &axisA = helicalAxis.getChain("A").getAtomPointers();
	AtomPointerVector &axisB = helicalAxis.getChain("B").getAtomPointers();

	/*****************************************************************************
	 *              === LOAD ROTAMERS FOR MONOMER & SET-UP SPM ===
	 ******************************************************************************/
	//Random Number Generator/
	RandomNumberGenerator RNG;
	//RNG.setSeed(_opt.seed); 
	RNG.setTimeBasedSeed();

	CSBMono.updateNonBonded(10,12,50);
	monoSys.buildAllAtoms();

	//loadRotamers(monoSys, monoRot, _opt.SL);
	loadMonomerRotamers(monoSys, monoRot);
	
	// Optimize Initial Starting Position (using Baseline to get back to original result)
	SelfPairManager monoSpm;
	monoSpm.seed(RNG.getSeed());
	monoSpm.setSystem(&monoSys);
	monoSpm.setVerbose(false);
	monoSpm.getMinStates()[0];
	monoSpm.updateWeights();
	monoSpm.setOnTheFly(true);
	monoSpm.saveEnergiesByTerm(true);
	monoSpm.calculateEnergies();

	repackSideChains(monoSpm, _opt.greedyCycles);

	monoSys.setActiveRotamers(monoSpm.getMinStates()[0]);

	monoSys.saveAltCoor("savedBestState");
	helicalAxis.saveAltCoor("BestAxis");

	/******************************************************************************
	 *                     === INITIAL VARIABLE SET UP ===
	 ******************************************************************************/
	AtomPointerVector &chainA = monoSys.getAtomPointers();

	/******************************************************************************
	 *                     === SHIFT HELICES INTO MEMBRANE ===
	 ******************************************************************************/
	CartesianPoint moveAxisBOneAngstrom;
	moveAxisBOneAngstrom.setCoor(1.0, 0.0, 0.0);
	_trans.translate(axisB, moveAxisBOneAngstrom);
	
	monoSys.calcEnergy();

	// move center of mass to origin
	//moveZCenterOfCAMassToOrigin(chainA, helicalAxis.getAtomPointers(), _trans);
	AtomSelection sel(chainA);
	monoSys.calcEnergy();

	// move center of mass to origin
	AtomPointerVector & caApV = sel.select("name CA");
	double centerHelix = 0.0;
	for(int i = 0; i < caApV.size(); i++) {
		centerHelix += (caApV[i]->getCoor()).getZ();
	}
	centerHelix = -1.0 * centerHelix/double(caApV.size());

	CartesianPoint interDistVect;
	interDistVect.setCoor(0.0, 0.0, centerHelix);
	_trans.translate(chainA, interDistVect);

	// Initial Z Shift move -5A down
	CartesianPoint zUnitVector;
	zUnitVector.setCoor(0.0, 0.0, 1.0);

	CartesianPoint move5Down = zUnitVector * -5.0;
	_trans.translate(chainA, move5Down);
	double bestZ = -5.0;

	monoSys.calcEnergy();
	
	// Repack side chains
	monoSpm.setOnTheFly(1);
	monoSpm.calculateEnergies();
        monoSpm.runGreedyOptimizer(_greedyCycles);

	double currentEnergy = monoSpm.getMinBound()[0];
	double bestEnergy = currentEnergy;
	monoSys.setActiveRotamers(monoSpm.getMinStates()[0]);
	monoSys.saveAltCoor("savedBestMonomer");
	helicalAxis.saveAltCoor("BestMonomerAxis");
	//_fout << "current Z: -5 Energy: " << currentEnergy*2.0 << endl; // must double the energy, as only computed energy for 1 helix

	// Test -5 to +5A shifts in Membrane
	for(int i=0; i<=10; i++) {

		_trans.translate(chainA, zUnitVector);

		//double currentZ = -5.0 + ((i+1)*1.0); 
		monoSpm.calculateEnergies();
		monoSpm.runGreedyOptimizer(_greedyCycles);
		currentEnergy = monoSpm.getMinBound()[0];
		//_fout << "current Z: " << currentZ << " Energy: " << currentEnergy*2.0 << endl; // must double the energy, as only computed energy for 1 helix

		if(currentEnergy < bestEnergy) {
			bestEnergy = currentEnergy;
			monoSys.setActiveRotamers(monoSpm.getMinStates()[0]);
			monoSys.saveAltCoor("savedBestMonomer");
			bestZ = -5.0 + ((i+1)*1.0);
		}
	}

	// Test at different tilts and rotations
	monoSys.applySavedCoor("savedBestMonomer");
	helicalAxis.applySavedCoor("BestMonomerAxis");

	monoSys.saveAltCoor("bestZ");
	helicalAxis.saveAltCoor("bestZ");

	double bestTilt = 0.0;
	double bestRotation = 0.0;
	double monoTilt = 0.0;
	double monoAxialRotation = 0.0;
	for(int i=1; i<=3; i++) { // test at 3 tilts: 15, 30 and 45 degrees
		//==================================
		//====== Membrane Tilt ======
		//==================================
		monoSys.applySavedCoor("bestZ");
		helicalAxis.applySavedCoor("bestZ");

		monoTilt = i * 15;
		_trans.rotate(chainA, monoTilt, axisA(0).getCoor(), axisB(0).getCoor());
		_trans.rotate(axisA, monoTilt, axisA(0).getCoor(), axisB(0).getCoor());
		for(int j=0; j<=3; j++) { // test at 4 rotations 0, 90, 180 and 270 degrees
			//==================================
			//====== Axial Rot ======
			//==================================
			monoAxialRotation = j * 90.0;

			monoSpm.calculateEnergies();
			monoSpm.runGreedyOptimizer(_greedyCycles);
			currentEnergy = monoSpm.getMinBound()[0];
			//_fout << "current tilt: " << monoTilt << " current rotation: " << monoAxialRotation << " Energy: " << currentEnergy*2.0 << endl; // must double the energy, as only computed energy for 1 helix
			//monoSys.writePdb("mono_" + MslTools::doubleToString(monoTilt) + "_" + MslTools::doubleToString(monoAxialRotation) + ".pdb");

			if(currentEnergy < bestEnergy) {
				bestEnergy = currentEnergy;
				bestTilt = monoTilt;
				bestRotation = monoAxialRotation;
				monoSys.setActiveRotamers(monoSpm.getMinStates()[0]);
				monoSys.saveAltCoor("savedBestMonomer");
				helicalAxis.saveAltCoor("BestMonomerAxis");
			}

			_trans.rotate(chainA, 90.0, axisA(0).getCoor(), axisA(1).getCoor());
			
		}
	}

	MonteCarloManager MCMngr(1000.0, 0.5, _MCCycles, MonteCarloManager::EXPONENTIAL, _MCMaxRejects);
	MCMngr.setEner(bestEnergy);

	double zShift = bestZ;
	double crossingAngle = bestTilt;
	double axialRotation = bestRotation;
	unsigned int counter = 0;

	while(!MCMngr.getComplete()) {

		monoSys.applySavedCoor("savedBestMonomer");
		helicalAxis.applySavedCoor("BestMonomerAxis");

		int moveToPreform = _RNG.getRandomInt(2);

		double deltaZShift = 0.0;
		double deltaTilt = 0.0;
		double deltaAxialRotation = 0.0;

		//======================================
		//====== Z Shift ======
		//======================================
		if (moveToPreform == 0) {
			deltaZShift = getStandardNormal(_RNG) * 1.0;
			CartesianPoint translateA = axisA(1).getCoor() - axisA(0).getCoor(); // vector minus helical center 
			translateA = translateA.getUnit() * deltaZShift; // unit vector of helical _axis times the amount to shift by
			_trans.translate(chainA, translateA);
			//_fout << setiosflags(ios::fixed) << setprecision(3)<< "Zshift: " << deltaZShift << endl;

		} else if (moveToPreform == 1) {
		//==================================
		//====== Axial Rot ======
		//==================================
			deltaAxialRotation = getStandardNormal(_RNG) * 20.0;
			_trans.rotate(chainA, deltaAxialRotation, axisA(0).getCoor(), axisA(1).getCoor());
			//_fout << setiosflags(ios::fixed) << setprecision(3)<< "axial: " << deltaAxialRotation << endl;

		} else if (moveToPreform == 2) {
		//==================================
		//====== Membrane Tilt ======
		//==================================
			deltaTilt = getStandardNormal(_RNG) * 10;
			_trans.rotate(chainA, deltaTilt, axisA(0).getCoor(), axisB(0).getCoor());
			_trans.rotate(axisA, deltaTilt, axisA(0).getCoor(), axisB(0).getCoor());
			//_fout << setiosflags(ios::fixed) << setprecision(3)<< "tilt: " << deltaTilt << endl;
		}

		// Run Optimization
		// Run repack every N steps
		if (counter % 10 == 0) {
			//_fout << "repack." << endl;
			monoSpm.calculateEnergies();
			monoSpm.runGreedyOptimizer(_greedyCycles);

			currentEnergy = monoSpm.getMinBound()[0];
		} else {
			currentEnergy = monoSys.calcEnergy();
			//_fout << monoEset->getSummary() << endl;
		}

		if (!MCMngr.accept(currentEnergy)) {
			//_fout << "state rejected   energy: " << currentEnergy << endl;
		}
		else {
			monoSys.setActiveRotamers(monoSpm.getMinStates()[0]);
			monoSys.saveAltCoor("savedBestMonomer");
			helicalAxis.saveAltCoor("BestMonomerAxis");
			bestEnergy = currentEnergy;

			crossingAngle = crossingAngle + deltaTilt;
			axialRotation = axialRotation + deltaAxialRotation;
			zShift = zShift +  deltaZShift;

			//_fout << setiosflags(ios::fixed) << setprecision(3) << "MCAccept   axial Tilt: " << crossingAngle << " zShift: " << zShift << " axialRot: " << axialRotation << " energy: " << currentEnergy*2 << endl;
		}

		counter++;
	}

	/******************************************************************************
	 *               === PRINT OUT MONOMER / STORE ENERGIES ===
	 ******************************************************************************/
	monoSys.applySavedCoor("savedBestMonomer");
	helicalAxis.applySavedCoor("BestMonomerAxis");
	monoSys.calcEnergy();

	double monomerEnergy = 2.0 * monoSpm.getMinBound()[0]; // double the energy for 2 helices
	double imm1 = (monoEset->getTermEnergy("CHARMM_IMM1")+monoEset->getTermEnergy("CHARMM_IMM1REF"))*2.0;
	//vector<double> self = calcBaselineEnergies(monoSys, 21, _opt.thread);
	//vector<double> pair = calcPairBaselineEnergies(monoSys, 21, _opt.thread);
	//double monomerSelf = sumEnergyVector(self)*2.0;
	//double monomerPair = sumEnergyVector(pair)*2.0;
	
	vector<uint> stateVec = monoSpm.getMinStates()[0];
	map<string,double> &energyMap = _seqEnergyMap[_seq];
	outputEnergiesByTerm(monoSpm, stateVec, energyMap, _opt.energyTermList, "Monomer", 1);
	//if (!_opt.energyLandscape){
	//	for (uint i=0; i<_opt.energyTermList.size(); i++){
	//		if (_opt.energyTermList[i] == "CHARMM_IMM1" || _opt.energyTermList[i] == "CHARMM_IMM1"){
	//			_seqEnergyMap[_seq]["IMM1Monomer"] = imm1;
	//		}
	//		else{
	//			string energyTerm = _opt.energyTermList[i];
	//			string energyLabel = energyTerm.substr(7,energyTerm.length())+"Monomer";
	//			_seqEnergyMap[_seq][energyLabel] = monoEset->getTermEnergy(_opt.energyTermList[i])*2;
	//		}
	//	}
	//	_seqEnergyMap[_seq]["Monomer"] = monomerEnergy;
	//}
	//else{
	//	_seqEnergyMap[_seq]["Monomer"] = monomerEnergy;
	//}
	return monomerEnergy;
}

void backboneMovement(AtomPointerVector & _chainA, AtomPointerVector & _chainB, AtomPointerVector & _axisA, AtomPointerVector & _axisB, Transforms _trans, double _deltaMove, unsigned int moveType) {
	 if (moveType == 0) {
		// Z Shift
		CartesianPoint translateA = _axisA(1).getCoor() - _axisA(0).getCoor(); // vector minus helical center 
		translateA = translateA.getUnit() * _deltaMove; // unit vector of helical _axis times the amount to shift by

		_trans.translate(_chainA, translateA);

		c2Symmetry(_chainA, _chainB);
		c2Symmetry(_axisA, _axisB);

	} else if (moveType == 1) {
		// Axial Rotation
		_trans.rotate(_chainA, (_deltaMove), _axisA(0).getCoor(), _axisA(1).getCoor());

		c2Symmetry(_chainA, _chainB);
		c2Symmetry(_axisA, _axisB);

	} else 	if (moveType == 2) {
		// Crossing Angle 
		_trans.rotate(_chainA, (_deltaMove * 0.5), _axisA(0).getCoor(), _axisB(0).getCoor());
		_trans.rotate(_axisA, (_deltaMove * 0.5), _axisA(0).getCoor(), _axisB(0).getCoor());

		c2Symmetry(_chainA, _chainB);
		c2Symmetry(_axisA, _axisB);

	} else if (moveType == 3) {
		// XShift
		// Helix A interhelical distance
		CartesianPoint translateA = _axisB(0).getCoor() - _axisA(0).getCoor(); // vector minus helical center 
		translateA = translateA.getUnit() * _deltaMove * -0.5; // unit vector of helical axis times the amount to shift by
		_trans.translate(_chainA, translateA);
		_trans.translate(_axisA, translateA);

		// Helix B interhelical distance
		c2Symmetry(_chainA, _chainB);
		c2Symmetry(_axisA, _axisB);

	} else {
		cerr << "Unknown moveType " << moveType << " in backboneMovement. Should be 0-3 " << endl;
	}
}

void xShiftTransformation(AtomPointerVector & _chainA, AtomPointerVector & _chainB, AtomPointerVector & _axisA, AtomPointerVector & _axisB, double _xShift, Transforms & _trans) {
	//====== X shift (Interhelical Distance) =======
	CartesianPoint interDistVect;
	interDistVect.setCoor((-1.0*_xShift/2.0), 0.0, 0.0);
	_trans.translate(_chainA, interDistVect);
	_trans.translate(_axisA, interDistVect);

	c2Symmetry(_chainA, _chainB);
	c2Symmetry(_axisA, _axisB);
}

//TODO: make below more elegant
void switchSystemSeq(System &_sys, string _seq){
	for (uint i=0; i<_seq.length(); i++){
		if (_sys.chainSize() == 1){
			string posA = _sys.getPosition(i).getPositionId();
			stringstream tmp;
			tmp << _seq[i];
			string aa = tmp.str();
			string resName = MslTools::getThreeLetterCode(aa);
			_sys.setActiveIdentity(posA, resName);//Not sure if these have to be linked again or if they still are?
		}
		else{
			string posA = _sys.getPosition(i).getPositionId();
			string posB = _sys.getChain("A").getPosition(i).getPositionId();
			stringstream tmp;
			tmp << _seq[i];
			string aa = tmp.str();
			string resName = MslTools::getThreeLetterCode(aa);
			_sys.setActiveIdentity(posA, resName);//Not sure if these have to be linked again or if they still are?
			_sys.setActiveIdentity(posB, resName);//Not sure if these have to be linked again or if they still are?
		}
	}
}

void saveEnergyDifference(Options _opt, map<string,map<string,double>> &_seqEnergyMap, string _sequence){
	map<string,double> &energyMap = _seqEnergyMap[_sequence];
	energyMap["Baseline-Monomer"] = energyMap["Baseline"] + energyMap["MonomerNoIMM1"];
	energyMap["HBONDDiff"] = energyMap["HBONDDimer"] - energyMap["HBONDMonomer"];
	energyMap["VDWDiff"] = energyMap["VDWDimer"] - energyMap["VDWMonomer"];
	energyMap["IMM1Diff"] = energyMap["IMM1Dimer"] - energyMap["IMM1Monomer"];
}

//Code Samson made a while back that should get each active ID and set a mask for anything that isn't active
std::vector < std::vector < bool > > getActiveMask (System &_sys) {
	_sys.updateVariablePositions();
	std::vector <unsigned int> residueState;
	std::vector < std::vector<unsigned int> > resRots(_sys.getMasterPositions().size());
	std::vector < std::vector<bool> > resMask(_sys.getMasterPositions().size());
	//Initialize residue state at the current active identity for each position
	for (unsigned int i = 0; i < _sys.getMasterPositions().size(); i++) {
		Position &pos = _sys.getPosition(_sys.getMasterPositions()[i]);
		unsigned int activeRes = pos.getActiveIdentity();
		residueState.push_back(activeRes);
		
		resRots[i] = std::vector<unsigned int> (pos.identitySize());
		for (unsigned int j = 0; j < pos.identitySize(); j++) {
			resRots[i][j] = pos.getTotalNumberOfRotamers(j);
		}
	}

	for (unsigned int i = 0; i < residueState.size(); i++) {
		unsigned int activeResidue = residueState[i];
		if (activeResidue >= resRots[i].size()) {
			cerr << "ERROR: the current residue number exceeds the number of residues for position " << i << endl;
			exit(100);
		}
		for (unsigned int j = 0; j < resRots[i].size(); j++) {
			if (j==activeResidue) {
				for (unsigned int k = 0; k < resRots[i][j]; k++) {
					resMask[i].push_back(true);
				}
			} else {
				for (unsigned int k = 0; k < resRots[i][j]; k++) {
					resMask[i].push_back(false);
				}
			}
		}
	
		//Sanity check for presence of true rotamers

		bool trueRots = false;
		for (unsigned int j = 0; j < resMask[i].size(); j++) {
			if (resMask[i][j]) {
				trueRots = true;
			}
		}
		if (!trueRots) {
			cerr << "ERROR AT POSITION: " << i << endl;
			cerr << "Current Residue: " << activeResidue << endl;
			cerr << "resRots at this position: " << endl;
			for (uint k = 0; k < resRots[i].size(); k++) {
				cerr << resRots[i][k] << " ";
			}
			cerr << endl;
			cerr << "resMask at this position: " << endl;
			for (uint k = 0; k < resMask[i].size(); k++) {
				cerr << resMask[i][k] << " ";
			}
			cerr << endl;	
			exit(9123);
		}
	}
	return resMask;
}

void calculateMonomerEnergiesNoMoves(PolymerSequence &_PL, Options &_opt, RandomNumberGenerator &_RNG, vector<string> &_seqs, map<string,map<string,double>> &_seqEnergyMap, vector<double> &_monomerEnergies, ofstream &_sout){
	
	System monoSys;
	CharmmSystemBuilder CSBMono(monoSys,_opt.topFile,_opt.parFile);
	CSBMono.setBuildTerm("CHARMM_ELEC", false);
	CSBMono.setBuildTerm("CHARMM_ANGL", false);
	CSBMono.setBuildTerm("CHARMM_BOND", false);
	CSBMono.setBuildTerm("CHARMM_DIHE", false);
	CSBMono.setBuildTerm("CHARMM_IMPR", false);
	CSBMono.setBuildTerm("CHARMM_U-BR", false);
	
	CSBMono.setBuildNonBondedInteractions(false);
	if(!CSBMono.buildSystem(_PL)) {
		cerr << "Unable to build system from " << _PL << endl;
		exit(0);
	} else {
		//fout << "CharmmSystem built for sequence" << endl;
	}
	
	/******************************************************************************
	 *                         === INITIALIZE POLYGLY ===
	 ******************************************************************************/
	// Read in Gly-69 to use as backbone coordinate template
	CRDReader cRead;
	cRead.open(_opt.backboneCrd); 
	if(!cRead.read()) {
		cerr << "Unable to read " << _opt.backboneCrd << endl;
		exit(0);
	}
	cRead.close();

	AtomPointerVector& glyAPV = cRead.getAtomPointers();//*/

	/******************************************************************************
	 *                         === INITIALIZE POLYGLY ===
	 ******************************************************************************/
	monoSys.assignCoordinates(glyAPV,false);
	monoSys.buildAllAtoms();

	CSBMono.updateNonBonded(10,12,50);

	SystemRotamerLoader monoRot(monoSys, _opt.rotLibFile);
	monoRot.defineRotamerSamplingLevels();

	// Add hydrogen bond term
	HydrogenBondBuilder monohb(monoSys, _opt.hBondFile);
	monohb.buildInteractions(50);

	/******************************************************************************
	 *                === DELETE TERMINAL HYDROGEN BOND INTERACTIONS ===
	 ******************************************************************************/
	deleteTerminalHydrogenBondInteractions(monoSys,_opt);
	
	/******************************************************************************
	 *                     === INITIAL VARIABLE SET UP ===
	 ******************************************************************************/
	EnergySet* EsetMono = monoSys.getEnergySet();
	// Set all terms active, besides Charmm-Elec
	EsetMono->setAllTermsActive();
	EsetMono->setTermActive("CHARMM_ELEC", false);
	EsetMono->setTermActive("CHARMM_ANGL", false);
	EsetMono->setTermActive("CHARMM_BOND", false);
	EsetMono->setTermActive("CHARMM_DIHE", false);
	EsetMono->setTermActive("CHARMM_IMPR", false);
	EsetMono->setTermActive("CHARMM_U-BR", false);
	EsetMono->setTermActive("SCWRL4_HBOND", true);
	
	/******************************************************************************
	 *             === SETUP ENERGY SET FOR MONOMER COMPARISON ===
	 ******************************************************************************/
	EsetMono->setWeight("CHARMM_VDW", 1);
	EsetMono->setWeight("SCWRL4_HBOND", 1);
	
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
		cout << "Unable to read axis" << endl;
		exit(0);
	}

	System helicalAxis;
	helicalAxis.addAtoms(readAxis.getAtomPointers());

	AtomPointerVector &axisA = helicalAxis.getChain("A").getAtomPointers();
	AtomPointerVector &axisB = helicalAxis.getChain("B").getAtomPointers();

	/******************************************************************************
	 *                  === GREEDY TO OPTIMIZE ROTAMERS ===
	 ******************************************************************************/
	//Random Number Generator/
	RandomNumberGenerator RNG;
	//RNG.setSeed(_opt.seed); 
	RNG.setTimeBasedSeed();
	
	CSBMono.updateNonBonded(10,12,50);
	monoSys.buildAllAtoms();
	
	loadRotamers(monoSys, monoRot, "SL95.00");//Baseline energies were calculated at the 95 rotamer level, so best to keep consistent
	
	// Optimize Initial Starting Position (using Baseline to get back to original result)
	SelfPairManager monoSpm;
	monoSpm.seed(RNG.getSeed());
	monoSpm.setSystem(&monoSys);
	monoSpm.setVerbose(false);
	monoSpm.getMinStates()[0];
	monoSpm.updateWeights();
	monoSpm.setOnTheFly(true);
	monoSpm.saveEnergiesByTerm(true);
	monoSpm.calculateEnergies();
	
	_sout << "***CALCULATE MONOMER ENERGY***" << endl << endl;
	monoSys.saveAltCoor("start");
	helicalAxis.saveAltCoor("start");
	for(uint i=0; i<_seqs.size(); i++){
		/******************************************************************************
		 *           === TRANSFORM HELICES TO INITIAL STARTING POSITION ===
		 ******************************************************************************/
		//Repack monomer
		switchSystemSeq(monoSys, _seqs[i]);
		vector<vector<bool>> mask = getActiveMask(monoSys);
		monoSpm.runGreedyOptimizer(_opt.greedyCycles, mask);
		monoSys.setActiveRotamers(monoSpm.getMinStates()[0]);
		vector<uint> stateVec = monoSpm.getMinStates()[0];
		monoSys.setActiveRotamers(stateVec);
		double monomerEnergy = monoSpm.getStateEnergy(stateVec);
		_sout << "Monomer Energy: " << monomerEnergy << endl << endl;

		// Add energy to sequence energy map
		map<string,double> &energyMap = _seqEnergyMap[_seqs[i]];
		outputEnergiesByTerm(monoSpm, stateVec, energyMap, _opt.energyTermList, "MonomerNoIMM1", 0);
		_seqEnergyMap[_seqs[i]]["MonomerNoIMM1"] = monomerEnergy*2;
		_monomerEnergies.push_back(monomerEnergy*2);
		cout << _seqs[i] << ": " << monomerEnergy*2 << endl;
	
		// Clear saved coordinates and reset to starting geometry
		monoSys.applySavedCoor("start");
		helicalAxis.applySavedCoor("start");
	}
}

//TODO: may need to add a scan in/do a 0 temp MC since it should be a gradient descent
void calculateMonomerEnergies(System &_sys, PolymerSequence &_PL, Options &_opt, Transforms & _trans, RandomNumberGenerator &_RNG, vector<string> &_seqs, map<string,map<string,double>> &_seqEnergyMap, vector<double> &_monomerEnergies, vector<int> &_allInterfacialPositions, ofstream &_sout){
	
	System monoSys;
	CharmmSystemBuilder CSBMono(monoSys,_opt.topFile,_opt.parFile,_opt.solvFile);
	CSBMono.setBuildTerm("CHARMM_ELEC", false);
	CSBMono.setBuildTerm("CHARMM_ANGL", false);
	CSBMono.setBuildTerm("CHARMM_BOND", false);
	CSBMono.setBuildTerm("CHARMM_DIHE", false);
	CSBMono.setBuildTerm("CHARMM_IMPR", false);
	CSBMono.setBuildTerm("CHARMM_U-BR", false);
	CSBMono.setBuildTerm("CHARMM_IMM1REF", true);
	CSBMono.setBuildTerm("CHARMM_IMM1", true);
	
	CSBMono.setSolvent("MEMBRANE");
	CSBMono.setIMM1Params(15, 10);
	
	CSBMono.setBuildNonBondedInteractions(false);
	if(!CSBMono.buildSystem(_PL)) {
		cerr << "Unable to build system from " << _PL << endl;
		exit(0);
	} 
	
	/******************************************************************************
	 *                         === INITIALIZE POLYGLY ===
	 ******************************************************************************/
	// Read in Gly-69 to use as backbone coordinate template
	CRDReader cRead;
	cRead.open(_opt.backboneCrd); 
	if(!cRead.read()) {
		cerr << "Unable to read " << _opt.backboneCrd << endl;
		exit(0);
	}
	cRead.close();

	AtomPointerVector& glyAPV = cRead.getAtomPointers();//*/

	/******************************************************************************
	 *                         === INITIALIZE POLYGLY ===
	 ******************************************************************************/
	monoSys.assignCoordinates(glyAPV,false);
	monoSys.buildAllAtoms();

	CSBMono.updateNonBonded(10,12,50);

	SystemRotamerLoader monoRot(monoSys, _opt.rotLibFile);
	monoRot.defineRotamerSamplingLevels();

	// Add hydrogen bond term
	HydrogenBondBuilder monohb(monoSys, _opt.hBondFile);
	monohb.buildInteractions(50);

	/******************************************************************************
	 *                === DELETE TERMINAL HYDROGEN BOND INTERACTIONS ===
	 ******************************************************************************/
	deleteTerminalHydrogenBondInteractions(monoSys,_opt);
	
	/******************************************************************************
	 *                     === INITIAL VARIABLE SET UP ===
	 ******************************************************************************/
	EnergySet* EsetMono = monoSys.getEnergySet();
	// Set all terms active, besides Charmm-Elec
	EsetMono->setAllTermsActive();
	EsetMono->setTermActive("CHARMM_ELEC", false);
	EsetMono->setTermActive("CHARMM_ANGL", false);
	EsetMono->setTermActive("CHARMM_BOND", false);
	EsetMono->setTermActive("CHARMM_DIHE", false);
	EsetMono->setTermActive("CHARMM_IMPR", false);
	EsetMono->setTermActive("CHARMM_U-BR", false);
	EsetMono->setTermActive("CHARMM_IMM1", true);
	EsetMono->setTermActive("CHARMM_IMM1REF", true);
	EsetMono->setTermActive("SCWRL4_HBOND", true);
	
	/******************************************************************************
	 *             === SETUP ENERGY SET FOR MONOMER COMPARISON ===
	 ******************************************************************************/
	EsetMono->setWeight("CHARMM_VDW", 1);
	EsetMono->setWeight("SCWRL4_HBOND", 1);
	EsetMono->setWeight("CHARMM_IMM1", 1);
	EsetMono->setWeight("CHARMM_IMM1REF", 1);
	
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
		cout << "Unable to read axis" << endl;
		exit(0);
	}

	System helicalAxis;
	helicalAxis.addAtoms(readAxis.getAtomPointers());

	AtomPointerVector &axisA = helicalAxis.getChain("A").getAtomPointers();
	AtomPointerVector &axisB = helicalAxis.getChain("B").getAtomPointers();

	/******************************************************************************
	 *                  === GREEDY TO OPTIMIZE ROTAMERS ===
	 ******************************************************************************/
	//Random Number Generator/
	RandomNumberGenerator RNG;
	//RNG.setSeed(_opt.seed); 
	RNG.setTimeBasedSeed();
	
	CSBMono.updateNonBonded(10,12,50);
	monoSys.buildAllAtoms();
	
	loadRotamers(monoSys, monoRot, _opt.SL);
	loadInterfacialRotamers(monoSys, monoRot, _opt.SLInterface, _allInterfacialPositions);
	
	CSBMono.updateNonBonded();
	monoSys.buildAllAtoms();
	// Optimize Initial Starting Position (using Baseline to get back to original result)
	SelfPairManager monoSpm;
	monoSpm.seed(RNG.getSeed());
	monoSpm.setSystem(&monoSys);
	monoSpm.setVerbose(false);
	monoSpm.getMinStates()[0];
	monoSpm.updateWeights();
	monoSpm.setOnTheFly(true);
	monoSpm.saveEnergiesByTerm(true);
	monoSpm.calculateEnergies();
	
	_sout << "***CALCULATE MONOMER ENERGY***" << endl << endl;
	monoSys.saveAltCoor("start");
	helicalAxis.saveAltCoor("start");
	for(uint i=0; i<_seqs.size(); i++){
		/******************************************************************************
		 *           === TRANSFORM HELICES TO INITIAL STARTING POSITION ===
		 ******************************************************************************/
		//monoSys.assignCoordinates(glyAPV,false);
		//monoSys.buildAllAtoms();
		
		//Repack monomer
		switchSystemSeq(monoSys, _seqs[i]);
		vector<vector<bool>> mask = getActiveMask(monoSys);
		monoSpm.runGreedyOptimizer(_opt.greedyCycles, mask);
		monoSys.setActiveRotamers(monoSpm.getMinStates()[0]);

		/******************************************************************************
		 *                     === INITIAL VARIABLE SET UP ===
		 ******************************************************************************/
		AtomPointerVector &chainA = monoSys.getAtomPointers();
	
		/******************************************************************************
		 *                     === SHIFT HELICES INTO MEMBRANE ===
		 ******************************************************************************/
		CartesianPoint moveAxisBOneAngstrom;
		moveAxisBOneAngstrom.setCoor(1.0, 0.0, 0.0);
		_trans.translate(axisB, moveAxisBOneAngstrom);
		
		monoSys.calcEnergy();
	
		// move center of mass to origin
		//moveZCenterOfCAMassToOrigin(chainA, helicalAxis.getAtomPointers(), _trans);
		AtomSelection sel(chainA);
		monoSys.calcEnergy();
	
		// move center of mass to origin
		AtomPointerVector & caApV = sel.select("name CA");
		double centerHelix = 0.0;
		for(int i = 0; i < caApV.size(); i++) {
			centerHelix += (caApV[i]->getCoor()).getZ();
		}
		centerHelix = -1.0 * centerHelix/double(caApV.size());
	
		CartesianPoint interDistVect;
		interDistVect.setCoor(0.0, 0.0, centerHelix);
		_trans.translate(chainA, interDistVect);
	
		// Initial Z Shift move -5A down
		CartesianPoint zUnitVector;
		zUnitVector.setCoor(0.0, 0.0, 1.0);
	
		CartesianPoint move5Down = zUnitVector * -5.0;
		_trans.translate(chainA, move5Down);
		double bestZ = -5.0;
	
		monoSys.calcEnergy();
		
		// Repack side chains
		monoSpm.setOnTheFly(1);
		monoSpm.calculateEnergies();
	        monoSpm.runGreedyOptimizer(_opt.greedyCycles, mask);
	
		double currentEnergy = monoSpm.getMinBound()[0];
		double bestEnergy = currentEnergy;
		monoSys.setActiveRotamers(monoSpm.getMinStates()[0]);
		monoSys.saveAltCoor("savedBestMonomer");
		helicalAxis.saveAltCoor("BestMonomerAxis");
	
		// Test -5 to +5A shifts in Membrane
		for(int i=0; i<=10; i++) {
	
			_trans.translate(chainA, zUnitVector);
	
			//double currentZ = -5.0 + ((i+1)*1.0); 
			monoSpm.calculateEnergies();
	        	monoSpm.runGreedyOptimizer(_opt.greedyCycles, mask);
			currentEnergy = monoSpm.getMinBound()[0];
	
			if(currentEnergy < bestEnergy) {
				bestEnergy = currentEnergy;
				monoSys.setActiveRotamers(monoSpm.getMinStates()[0]);
				monoSys.saveAltCoor("savedBestMonomer");
				bestZ = -5.0 + ((i+1)*1.0);
			}
		}
	
		// Test at different tilts and rotations
		monoSys.applySavedCoor("savedBestMonomer");
		helicalAxis.applySavedCoor("BestMonomerAxis");
	
		monoSys.saveAltCoor("bestZ");
		helicalAxis.saveAltCoor("bestZ");
	
		double bestTilt = 0.0;
		double bestRotation = 0.0;
		double monoTilt = 0.0;
		double monoAxialRotation = 0.0;
		for(int i=1; i<=3; i++) { // test at 3 tilts: 15, 30 and 45 degrees
			//==================================
			//====== Membrane Tilt ======
			//==================================
			monoSys.applySavedCoor("bestZ");
			helicalAxis.applySavedCoor("bestZ");
	
			monoTilt = i * 15;
			_trans.rotate(chainA, monoTilt, axisA(0).getCoor(), axisB(0).getCoor());
			_trans.rotate(axisA, monoTilt, axisA(0).getCoor(), axisB(0).getCoor());
			for(int j=0; j<=3; j++) { // test at 4 rotations 0, 90, 180 and 270 degrees
				//==================================
				//====== Axial Rot ======
				//==================================
				monoAxialRotation = j * 90.0;
	
				monoSpm.calculateEnergies();
	        		monoSpm.runGreedyOptimizer(_opt.greedyCycles, mask);
				currentEnergy = monoSpm.getMinBound()[0];
				//monoSys.writePdb("mono_" + MslTools::doubleToString(monoTilt) + "_" + MslTools::doubleToString(monoAxialRotation) + ".pdb");
	
				if(currentEnergy < bestEnergy) {
					bestEnergy = currentEnergy;
					bestTilt = monoTilt;
					bestRotation = monoAxialRotation;
					monoSys.setActiveRotamers(monoSpm.getMinStates()[0]);
					monoSys.saveAltCoor("savedBestMonomer");
					helicalAxis.saveAltCoor("BestMonomerAxis");
				}
	
				_trans.rotate(chainA, 90.0, axisA(0).getCoor(), axisA(1).getCoor());
				
			}
		}
	
		//MonteCarloManager MCMngr(1000.0, 0.5, _opt.MCCycles, MonteCarloManager::EXPONENTIAL, _opt.MCMaxRejects);
		//MonteCarloManager MCMngr(1000.0, 0.5, 100, MonteCarloManager::EXPONENTIAL, 50);
		MonteCarloManager MCMngr(0, 0, 100, 4, 1);
		MCMngr.setEner(bestEnergy);
	
		double zShift = bestZ;
		double crossingAngle = bestTilt;
		double axialRotation = bestRotation;
		unsigned int counter = 0;
	
		while(!MCMngr.getComplete()) {
	
			monoSys.applySavedCoor("savedBestMonomer");
			helicalAxis.applySavedCoor("BestMonomerAxis");
	
			int moveToPreform = _RNG.getRandomInt(2);
	
			double deltaZShift = 0.0;
			double deltaTilt = 0.0;
			double deltaAxialRotation = 0.0;
	
			//======================================
			//====== Z Shift ======
			//======================================
			if (moveToPreform == 0) {
				deltaZShift = getStandardNormal(_RNG) * 1.0;
				CartesianPoint translateA = axisA(1).getCoor() - axisA(0).getCoor(); // vector minus helical center 
				translateA = translateA.getUnit() * deltaZShift; // unit vector of helical _axis times the amount to shift by
				_trans.translate(chainA, translateA);
	
			} else if (moveToPreform == 1) {
			//==================================
			//====== Axial Rot ======
			//==================================
				deltaAxialRotation = getStandardNormal(_RNG) * 20.0;
				_trans.rotate(chainA, deltaAxialRotation, axisA(0).getCoor(), axisA(1).getCoor());
	
			} else if (moveToPreform == 2) {
			//==================================
			//====== Membrane Tilt ======
			//==================================
				deltaTilt = getStandardNormal(_RNG) * 10;
				_trans.rotate(chainA, deltaTilt, axisA(0).getCoor(), axisB(0).getCoor());
				_trans.rotate(axisA, deltaTilt, axisA(0).getCoor(), axisB(0).getCoor());
			}
	
			// Run Optimization
			// Run repack every N steps
			if (counter % 10 == 0) {
				monoSpm.calculateEnergies();
	        		monoSpm.runGreedyOptimizer(_opt.greedyCycles, mask);
	
				currentEnergy = monoSpm.getMinBound()[0];
			} else {
				currentEnergy = monoSys.calcEnergy();
			}
	
			if (!MCMngr.accept(currentEnergy)) {
				//_sout << "state rejected   energy: " << currentEnergy << endl;
			}
			else {
				monoSys.setActiveRotamers(monoSpm.getMinStates()[0]);
				monoSys.saveAltCoor("savedBestMonomer");
				helicalAxis.saveAltCoor("BestMonomerAxis");
				bestEnergy = currentEnergy;
	
				crossingAngle = crossingAngle + deltaTilt;
				axialRotation = axialRotation + deltaAxialRotation;
				zShift = zShift +  deltaZShift;
	

				//_sout << setiosflags(ios::fixed) << setprecision(3) << "MCAccept   axial Tilt: " << crossingAngle << " zShift: " << zShift << " axialRot: " << axialRotation << " energy: " << currentEnergy*2 << endl;
			}


			//TODO: need to eventually just rid of this distinction: output a normal file AND an energy landscape file
			//if (!_opt.energyLandscape){
			//	double imm1 = EsetMonomer->getTermEnergy("CHARMM_IMM1REF")+EsetMonomer->getTermEnergy("CHARMM_IMM1");
			//	for (uint i=0; i<_opt.energyTermList.size(); i++){
			//		if (_opt.energyTermList[i] == "CHARMM_IMM1REF" || _opt.energyTermList[i] == "CHARMM_IMM1"){
			//			_seqEnergyMap[_seqs[i]]["IMM1Monomer"] = imm1;
			//		}
			//		else{
			//			string energyTerm = _opt.energyTermList[i];
			//			string energyLabel = energyTerm.substr(7,energyTerm.length())+"Monomer";
			//			_seqEnergyMap[_seqs[i]][energyLabel] = EsetMonomer->getTermEnergy(_opt.energyTermList[i]);
			//		}
			//	}
			//	_seqEnergyMap[_seqs[i]]["Monomer"] = monomerEnergy;
			//}
			//else{
			//	_seqEnergyMap[_seqs[i]]["Monomer"] = monomerEnergy;
			//	_monomerEnergies.push_back(monomerEnergy);
			//}
			counter++;

		}
		cout << setiosflags(ios::fixed) << setprecision(3) << "MCAccept   axial Tilt: " << crossingAngle << " zShift: " << zShift << " axialRot: " << axialRotation << " energy: " << currentEnergy*2 << endl;

		//Calculate Monomer energy for output
		monoSys.applySavedCoor("savedBestMonomer");
		helicalAxis.applySavedCoor("BestMonomerAxis");
	        monoSpm.runGreedyOptimizer(_opt.greedyCycles, mask);
		vector<uint> stateVec = monoSpm.getMinStates()[0];
		monoSys.setActiveRotamers(stateVec);
		double monomerEnergy = monoSpm.getStateEnergy(stateVec);
		_sout << "Monomer Energy: " << monomerEnergy << endl << endl;

		// Add energy to sequence energy map
		map<string,double> &energyMap = _seqEnergyMap[_seqs[i]];
		outputEnergiesByTerm(monoSpm, stateVec, energyMap, _opt.energyTermList, "Monomer", 1);
		_seqEnergyMap[_seqs[i]]["Monomer"] = monomerEnergy*2;
		_monomerEnergies.push_back(monomerEnergy*2);
		cout << _seqs[i] << ": " << monomerEnergy*2 << endl;
	
		// Clear saved coordinates and reset to starting geometry
		monoSys.clearSavedCoor("savedBestMonomer");
		monoSys.clearSavedCoor("bestZ");
		helicalAxis.clearSavedCoor("BestMonomerAxis");
		helicalAxis.clearSavedCoor("bestZ");
		monoSys.applySavedCoor("start");
		helicalAxis.applySavedCoor("start");
	}
}

void localMC(System &_sys, System &_helicalAxis, Options &_opt, PolymerSequence &_PL, RandomNumberGenerator &_RNG, vector<string> &_seqs, vector<int> &_allInterfacialPositions, vector<vector<string>> &_linkedPos, map<string,map<string,double>> &_seqEnergyMap, vector<double> &_monomerEnergies, vector<double> &_dimerEnergies, vector<double> &_finalEnergies, vector<double> &_xShifts, vector<double> &_crossingAngles, vector<double> &_axialRotations, vector<double> &_zShifts, ofstream &_sout, ofstream &_err, PDBWriter &_writer){
	
	System sysDimer;
	CharmmSystemBuilder CSBDimer(sysDimer,_opt.topFile,_opt.parFile,_opt.solvFile);
	CSBDimer.setBuildTerm("CHARMM_ELEC", false);
	CSBDimer.setBuildTerm("CHARMM_ANGL", false);
	CSBDimer.setBuildTerm("CHARMM_BOND", false);
	CSBDimer.setBuildTerm("CHARMM_DIHE", false);
	CSBDimer.setBuildTerm("CHARMM_IMPR", false);
	CSBDimer.setBuildTerm("CHARMM_U-BR", false);
	CSBDimer.setBuildTerm("CHARMM_IMM1REF", true);
	CSBDimer.setBuildTerm("CHARMM_IMM1", true);
	
	CSBDimer.setSolvent("MEMBRANE");
	CSBDimer.setIMM1Params(15, 10);
	
	CSBDimer.setBuildNonBondedInteractions(false);
	if(!CSBDimer.buildSystem(_PL)) {
		cerr << "Unable to build system from " << _PL << endl;
		exit(0);
	}
	
	Chain & chainA = sysDimer.getChain("A");
	Chain & chainB = sysDimer.getChain("B");

	// Set up chain A and chain B atom pointer vectors
	AtomPointerVector & apvChainA = chainA.getAtomPointers();
	AtomPointerVector & apvChainB = chainB.getAtomPointers();

	/******************************************************************************
	 *           === TRANSFORM HELICES TO INITIAL STARTING POSITION ===
	 ******************************************************************************/
	sysDimer.assignCoordinates(_sys.getAtomPointers(),false);
	sysDimer.buildAllAtoms();
	
	SystemRotamerLoader sysDimerRot(sysDimer, _opt.rotLibFile);
	sysDimerRot.defineRotamerSamplingLevels();
	
	HydrogenBondBuilder hb(sysDimer, _opt.hBondFile);
	hb.buildInteractions(50);//when this is here, the HB weight is correct
	
	/******************************************************************************
	 *                === DELETE TERMINAL HYDROGEN BOND INTERACTIONS ===
	 ******************************************************************************/
	deleteTerminalHydrogenBondInteractions(sysDimer,_opt);
	
	/******************************************************************************
	 *                     === INITIAL VARIABLE SET UP ===
	 ******************************************************************************/
	EnergySet* EsetDimer = sysDimer.getEnergySet();
	// Set all terms active, besides Charmm-Elec
	EsetDimer->setAllTermsActive();
	EsetDimer->setTermActive("CHARMM_ELEC", false);
	EsetDimer->setTermActive("CHARMM_ANGL", false);
	EsetDimer->setTermActive("CHARMM_BOND", false);
	EsetDimer->setTermActive("CHARMM_DIHE", false);
	EsetDimer->setTermActive("CHARMM_IMPR", false);
	EsetDimer->setTermActive("CHARMM_U-BR", false);
	EsetDimer->setTermActive("CHARMM_IMM1", true);
	EsetDimer->setTermActive("CHARMM_IMM1REF", true);
	EsetDimer->setTermActive("SCWRL4_HBOND", true);
	
	/******************************************************************************
	 *             === SETUP ENERGY SET FOR MONOMER COMPARISON ===
	 ******************************************************************************/
	EsetDimer->setWeight("CHARMM_VDW", 1);
	EsetDimer->setWeight("SCWRL4_HBOND", 1);
	EsetDimer->setWeight("CHARMM_IMM1", 1);
	EsetDimer->setWeight("CHARMM_IMM1REF", 1);

	/******************************************************************************
	 *                     === SET UP TRANSFORMS OBJECT ===
	 ******************************************************************************/
	Transforms trans;
	trans.setTransformAllCoors(true); // transform all coordinates (non-active rotamers)
	trans.setNaturalMovements(true); // all atoms are rotated such as the total movement of the atoms is minimized
	
	/******************************************************************************
	 *                  === GREEDY TO OPTIMIZE ROTAMERS ===
	 ******************************************************************************/
	CSBDimer.updateNonBonded(10,12,50);
	sysDimer.buildAllAtoms();
	
	sysDimer.setLinkedPositions(_linkedPos);//TODO: changed this on 08_01_2021 to see if this is the problem with this function; sumber of rotamer in a position is too high, but why would linked have to do with it?
	
	loadRotamers(sysDimer, sysDimerRot, _opt.SL);
	loadInterfacialRotamers(sysDimer, sysDimerRot, _opt.SLInterface, _allInterfacialPositions);
	
	// Optimize Initial Starting Position (using Baseline to get back to original result)
	SelfPairManager spmDimer;
	spmDimer.seed(_RNG.getSeed());
	spmDimer.setSystem(&sysDimer);
	spmDimer.setVerbose(false);
	spmDimer.getMinStates()[0];
	spmDimer.updateWeights();
	spmDimer.setOnTheFly(true);
	spmDimer.saveEnergiesByTerm(true);
	spmDimer.calculateEnergies();
	
	_sout << "***CALCULATE DIMER ENERGY WITHOUT LOCAL REPACK***" << endl << endl;
	
	sysDimer.saveAltCoor("start");
	_helicalAxis.saveAltCoor("start");
	
	time_t startTimeMC, endTimeMC;
	double diffTimeMC;
	time(&startTimeMC);
	
	//for(uint i=0; i<_seqs.size(); i++){
	for(uint i=0; i<_seqs.size(); i++){
		string sequence = _seqs[i];	
		//Repack dimer
		switchSystemSeq(sysDimer, sequence);
		vector<vector<bool>> mask = getActiveMask(sysDimer);
		spmDimer.runGreedyOptimizer(100, mask);
		vector<uint> stateVec = spmDimer.getMinStates()[0];
		sysDimer.setActiveRotamers(stateVec);
		
		sysDimer.saveAltCoor("savedBestState");
		_helicalAxis.saveAltCoor("BestAxis");
		cout << EsetDimer->getSummary() << endl;
	
		/******************************************************************************
		 *                     === HELICAL AXIS SET UP ===
		 ******************************************************************************/
		AtomPointerVector &axisA = _helicalAxis.getChain("A").getAtomPointers();
		AtomPointerVector &axisB = _helicalAxis.getChain("B").getAtomPointers();
		
		// Reference points for Helices
		CartesianPoint ori(0.0,0.0,0.0);
		CartesianPoint zAxis(0.0,0.0,1.0);
		CartesianPoint xAxis(1.0,0.0,0.0);
	
		/******************************************************************************
		 *                     === INITIAL STARTING POSITION ===
		 ******************************************************************************/
		double xShift = _opt.xShift;
		double crossingAngle = _opt.crossingAngle;
		double axialRotation = _opt.axialRotation;
		double zShift = _opt.zShift;
	
		_sout << setiosflags(ios::fixed) << setprecision(3) << "Starting parameters: crossingAngle: " << crossingAngle << " axialRotation: " << axialRotation << " zShift: " << zShift;
		_sout << " xShift: " << xShift << endl << endl;
	
		sysDimer.setActiveRotamers(stateVec);
		double currentEnergy = spmDimer.getMinBound()[0];
		double bestEnergy = currentEnergy;

		//Redacted for now as of 06_05_2021: docks the helices together
		/******************************************************************************
		 *                     === X SHIFT REPACKS ===
		 ******************************************************************************/
		/*double savedXShift = xShift;
		double previousEnergy = _monomerEnergy;
		double deltaXShift = -0.1;
		double globalLowestE = _monomerEnergy;
		double xShiftEnd = 7.5;//TODO: probably should change this to an option, or xShift-0.5 or something of the like
	
		
		if (crossingAngle < 0){
			xShiftEnd = 6.4;
		}
	
		//Redacted for now as of 06_05_2021: docks the helices together
		while (xShift >= xShiftEnd) {
		
			xShift += deltaXShift;
	
			// Move the helix
			backboneMovement(apvChainA, apvChainB, axisA, axisB, trans, deltaXShift, 3 );
			
			// Run Optimization
			repackSideChains(spmDimer, _opt.greedyCycles);
		
			vector<unsigned int> MCOFinal;
			MCOFinal = spmDimer.getMinStates()[0];
			sysDimer.setActiveRotamers(MCOFinal);
		
			cout << EsetDimer->getSummary() << endl;
			currentEnergy = spmDimer.getMinBound()[0];
		
			if (currentEnergy < bestEnergy) {
				bestEnergy = currentEnergy;
				savedXShift = xShift;
				sysDimer.saveAltCoor("savedBestState");
				_helicalAxis.saveAltCoor("BestAxis");
			}
		
			//_out << "xShift: " << xShift << " energy: " << currentEnergy-monomerEnergy << endl;
			cout << "xShift: " << xShift << " energy: " << currentEnergy-_monomerEnergy << endl;
	
			// If energy increase twice in a row, and it is above the global lowest energy, quit
			if (currentEnergy < globalLowestE) {
				globalLowestE = currentEnergy;
			}
			if (currentEnergy > (globalLowestE+10.0) && previousEnergy > (globalLowestE+10.0) && currentEnergy > previousEnergy) {
				//_out << "Energy increasing above global lowest energy... (currently " << globalLowestE-monomerEnergy << ")" << endl;
				break;	
			}
			else {
				previousEnergy = currentEnergy;
			}
		}*/ // redacted on 05_27_2021: decided to not do this; if a seqs[i] has to move too much it may not be a good fit for the backbone (and we may be docking later anyways)
		//cout << "Best Energy at x shift: " << bestEnergy-_monomerEnergy << " at " << savedXShift << endl; 
		//xShift = savedXShift;
	
		/******************************************************************************
		 *               === LOCAL BACKBONE MONTE CARLO REPACKS ===
		 ******************************************************************************/
	
		if (_opt.verbose){
			cout << "====================================" << endl;
			cout << "Performing Local Monte Carlo Repacks" << endl;
			cout << "====================================" << endl;
			cout << "Sequence #" << i << ": " << sequence << endl << endl;
		}

		vector<unsigned int> MCOBest = spmDimer.getMinStates()[0];
		
		if (_opt.MCCycles > 0) {
			//MonteCarloManager MCMngr(1000.0, 0.5, 100, MonteCarloManager::EXPONENTIAL, 5);
			//MonteCarloManager MCMngr(_opt.MCStartTemp, _opt.MCEndTemp, _opt.MCCycles, _opt.MCCurve, _opt.MCMaxRejects);
			MonteCarloManager MCMngr(0, 0, 250, 4, 1);//TODO: try this out to see if it's faster and still converges (trying to see if I'm running too many cycles
	
			MCMngr.setEner(bestEnergy);
			
			unsigned int counter = 0;
			while(!MCMngr.getComplete()) {
	
				sysDimer.applySavedCoor("savedBestState");
				_helicalAxis.applySavedCoor("BestAxis");
	
				int moveToPreform = _RNG.getRandomInt(3);
	
				double deltaXShift = 0.0;
				double deltaZShift = 0.0;
				double deltaCrossingAngle = 0.0;
				double deltaAxialRotation = 0.0; 
	
				//======================================
				//====== Z Shift (Crossing Point) ======
				//======================================
				if (moveToPreform == 0) {
					//deltaZShift = getStandardNormal(RNG1) * 0.1;
					deltaZShift = getStandardNormal(_RNG) * _opt.deltaZ;
					backboneMovement(apvChainA, apvChainB, axisA, axisB, trans, deltaZShift, moveToPreform);
				} else if (moveToPreform == 1) {
				//===========================
				//===== Axial Rotation ======
				//===========================
					//deltaAxialRotation = getStandardNormal(_RNG1) * 1.0;
					deltaAxialRotation = getStandardNormal(_RNG) * _opt.deltaAx;
					backboneMovement(apvChainA, apvChainB, axisA, axisB, trans, deltaAxialRotation, moveToPreform);
				} else if (moveToPreform == 2) {
				//==================================
				//====== Local Crossing Angle ======
				//==================================
					//deltaCrossingAngle = getStandardNormal(_RNG1) * 1.0;
					deltaCrossingAngle = getStandardNormal(_RNG) * _opt.deltaCross;
					backboneMovement(apvChainA, apvChainB, axisA, axisB, trans, deltaCrossingAngle, moveToPreform);
				} else if (moveToPreform == 3) {
				//==============================================
				//====== X shift (Interhelical Distance) =======
				//==============================================
					//deltaXShift = getStandardNormal(_RNG1) * 0.1;
					deltaXShift = getStandardNormal(_RNG) * _opt.deltaX;
					backboneMovement(apvChainA, apvChainB, axisA, axisB, trans, deltaXShift, moveToPreform);
				}
	
				// Calculate energy and compare to previous best
				spmDimer.calculateEnergies();
				spmDimer.runGreedyOptimizer(_opt.greedyCycles, mask);
				vector<unsigned int> MCOFinal = spmDimer.getMinStates()[0];
				sysDimer.setActiveRotamers(MCOFinal);
				currentEnergy = spmDimer.getStateEnergy(MCOFinal);
	
				// Run repack every N steps
				//if (counter % 5 == 0) {
				//	spmDimer.calculateEnergies();
	        		//	spmDimer.runGreedyOptimizer(_opt.greedyCycles, mask);
	
				//	currentEnergy = spmDimer.getMinBound()[0];
				//} else {
				//	currentEnergy = sysDimer.calcEnergy();
				//}

				if (!MCMngr.accept(currentEnergy)) {
					if (_opt.verbose){
						_sout << "state rejected   energy: " << currentEnergy-_monomerEnergies[i] << endl;
					}
				}
				else {
					bestEnergy = currentEnergy;
					sysDimer.saveAltCoor("savedBestState");
					_helicalAxis.saveAltCoor("BestAxis");
	
					xShift = xShift + deltaXShift;
					crossingAngle = crossingAngle + deltaCrossingAngle;
					axialRotation = axialRotation + deltaAxialRotation;
					zShift = zShift + deltaZShift;
					MCOBest = MCOFinal;
	
					if (_opt.verbose){
						_sout << "MCAccept   xShift: " << xShift << " crossingAngle: " << crossingAngle << " axialRotation: " << axialRotation << " zShift: " << zShift << " energy: " << currentEnergy-_monomerEnergies[i] << endl;
					}
				}
			counter++;
			}
		}
	
		sysDimer.applySavedCoor("savedBestState");

		double dimerEnergy = spmDimer.getStateEnergy(MCOBest);
		double monomerEnergy = _seqEnergyMap[sequence]["Monomer"];
		double finalEnergy = dimerEnergy-_monomerEnergies[i];

		// Print out info to the summary file
		_sout << "Sequence #" << i << " Geometry " << endl;
		_sout << "xShift: " << xShift << endl;
		_sout << "crossingAngle: " << crossingAngle << endl;
		_sout << "axialRotation: " << axialRotation << endl;
		_sout << "zShift: " << zShift << endl << endl;
		_sout << "Energy Summary Below" << endl;
		_sout << "Monomer Energy: " << _monomerEnergies[i] << endl;
		_sout << "Dimer Energy: " << sysDimer.calcEnergy() << endl;
		_sout << "Final Energy: " << finalEnergy << endl << endl;
		_sout << EsetDimer->getSummary() << endl << endl;
		cout << EsetDimer->getSummary() << endl << endl;
	
		// Add energies of the sequence to the energy map
		map<string,double> &energyMap = _seqEnergyMap[sequence];
		outputEnergiesByTerm(spmDimer, MCOBest, energyMap, _opt.energyTermList, "Dimer", 1);
		saveEnergyDifference(_opt, _seqEnergyMap, sequence);
		_seqEnergyMap[sequence]["Dimer"] = dimerEnergy;
		_seqEnergyMap[sequence]["Total"] = finalEnergy;
		_finalEnergies.push_back(finalEnergy);
		_dimerEnergies.push_back(dimerEnergy);
	
		// Add geometries to geometry vectors
		_xShifts.push_back(xShift);
		_crossingAngles.push_back(crossingAngle);
		_axialRotations.push_back(axialRotation);
		_zShifts.push_back(zShift);

		// Write pdb into file with all sequences
		_writer.write(sysDimer.getAtomPointers(),true,false,true);
		
		// Write an individual pdb for each sequence
		PDBWriter designWriter;
		designWriter.open(_opt.pdbOutputDir + "/design_" + MslTools::intToString(i) + ".pdb");
		designWriter.write(sysDimer.getAtomPointers(), true, false, true);
		designWriter.close();
	
		// Clear coordinates for and reset to the initial starting position
		sysDimer.clearSavedCoor("savedBestState");
		_helicalAxis.clearSavedCoor("BestAxis");
		sysDimer.applySavedCoor("start");
		_helicalAxis.applySavedCoor("start");
	}
	time(&endTimeMC);
	diffTimeMC = difftime (endTimeMC, startTimeMC);
	_sout << "Monte Carlo repack complete. Time: " << diffTimeMC << " seconds" << endl << endl;
	cout << "Monte Carlo repack complete. Time: " << diffTimeMC << " seconds" << endl << endl;
}

//Checks through a vector of sequences to see if the new sequence has already been found
bool sameSequenceChecker(string &_newSeq, vector<string> &_seqs){
	bool sameSeq = false;
	if (_seqs.size() == 0){
		_seqs.push_back(_newSeq);
	}
	else {
		for (int j=0; j<_seqs.size(); j++){
			//cout << _seqs[j] << " : " << _newSeq << ":" << sameSeq << endl;
			if (_seqs[j] == _newSeq){
				sameSeq = true;
				j = _seqs.size()-1;
			}
			else if (j==_seqs.size()-1){
				//cout << _seqs[j] << " : " << _newSeq << ":" << sameSeq << endl;
				if (sameSeq == false){
					_seqs.push_back(_newSeq);
					//cout << "Unique Seq " << ": " << _newSeq << endl;
					j = _seqs.size();
				}
			}
		}
	}
	return sameSeq;
}

//TODO: add the below functions to baseline files?
map<string, double> readSingleParameters(string _baselineFile){
	Reader selfReader(_baselineFile);
	selfReader.open();
	map<string, double> selfEnergies;

	if(!(selfReader.is_open())){
		cerr << "WARNING: Unable to open " << _baselineFile << endl;
		exit(0);
	}

	vector<string> lines = selfReader.getAllLines();

	for (int i=0; i<lines.size(); i++){
		vector<string> tokens = MslTools::tokenize(lines[i], "\t");
		if(tokens.size() < 1){
			continue;
		}
		if(tokens.size() != 2){
			cerr << "WARNING: Line\"" << lines[i] << "\" is not in FORMAT: ResName(string) Energy(double)";
			continue;
		}
		selfEnergies[MslTools::toUpper(tokens[0])] = MslTools::toDouble(tokens[1]);
		//cout << tokens[0] << " " << tokens[1] << " " << tokens[2] << " = " << tokens[3] << endl;
	}
	
	selfReader.close();
	return selfEnergies;
}

map<string,map<string,map<uint, double>>> readPairParameters(string _baselineFile){
	Reader pairReader(_baselineFile);
	pairReader.open();
	map<string,map<string,map<uint, double>>> pairEnergies;

	if(!(pairReader.is_open())){
		cerr << "WARNING: Unable to open " << _baselineFile << endl;
		exit(0);
	}

	vector<string> lines = pairReader.getAllLines();

	for (int i=0; i<lines.size(); i++){
		vector<string> tokens = MslTools::tokenize(lines[i], " ");
		if(tokens.size() < 1){
			continue;
		}
		if(tokens.size() != 4){
			cerr << "WARNING: Line\"" << lines[i] << "\" is not in FORMAT: ResName(string) ResName(string) Distance(uint) Energy(double)";
			continue;
		}
		if (tokens[0].compare(tokens[1]) == 0){//Added in on 03-18-2021: apparently the code that I was using to flip the AAs in buildPairInteractions isn't good, but this adds the flips to the map which works better and is cleaner
			pairEnergies[MslTools::toUpper(tokens[0])][MslTools::toUpper(tokens[1])][MslTools::toInt(tokens[2])] = MslTools::toDouble(tokens[3]);
		}
		else{
			pairEnergies[MslTools::toUpper(tokens[0])][MslTools::toUpper(tokens[1])][MslTools::toInt(tokens[2])] = MslTools::toDouble(tokens[3]);
			pairEnergies[MslTools::toUpper(tokens[1])][MslTools::toUpper(tokens[0])][MslTools::toInt(tokens[2])] = MslTools::toDouble(tokens[3]);
		}
	}
	
	pairReader.close();
	return pairEnergies;
}

//Based on the above function: Reads a Gaussian Kde file to be used to search for a density estimate to choose a spot in the geometric space for the run geometry
// This one is specifically for rotation and z shift
void getGaussianKdeValues(Options &_opt, double _kdeValue, double &_xShift, double &_crossingAngle, double &_axialRotation, double &_zShift, ofstream &_out){
	// Setup kde file reader
	Reader kdeReader(_opt.geometryDensityFile);
	kdeReader.open();
	map<double,vector<double>> kdeEnergies;

	if(!(kdeReader.is_open())){
		cerr << "WARNING: Unable to open " << _opt.geometryDensityFile << endl;
		exit(0);
	}

	vector<string> lines = kdeReader.getAllLines();

	for (int i=0; i<lines.size(); i++){
		vector<string> tokens = MslTools::tokenize(lines[i], "\t");
		if(tokens.size() < 1){
			continue;
		}
		if(tokens.size() != 7){
			cerr << "WARNING: Line\"" << lines[i] << "\" is not in FORMAT: KDE(double) xShift(double) Angle(double) Rot1(double) Rot2(double) Z1(double) Z2(double)";
			continue;
		}
		vector<double> geometries;
		geometries.push_back(MslTools::toDouble(tokens[1]));
		geometries.push_back(MslTools::toDouble(tokens[2]));
		geometries.push_back(MslTools::toDouble(tokens[3]));
		geometries.push_back(MslTools::toDouble(tokens[4]));
		geometries.push_back(MslTools::toDouble(tokens[5]));
		geometries.push_back(MslTools::toDouble(tokens[6]));
		kdeEnergies[MslTools::toDouble(tokens[0])] = geometries;
	}

	map<double,vector<double>>::iterator low;
	low = kdeEnergies.lower_bound(_kdeValue);
	_out << "Found kde value: " << low->first << endl;

	RandomNumberGenerator RNG;
	//RNG.setSeed(_opt.seed); 
	RNG.setTimeBasedSeed();

	int r = RNG.getRandomInt(2,3);
	int z = RNG.getRandomInt(4,5);

	_out << "xShift: " << kdeEnergies.at(low->first)[0] << endl;
	_out << "crossingAngle: " << kdeEnergies.at(low->first)[1] << endl;
	_out << "axialRotation: " << r-1 << "	" << kdeEnergies.at(low->first)[r] << endl; // subtract to get which column it's a part of
	_out << "zShift: " << z-3 << "	" << kdeEnergies.at(low->first)[z] << endl;
	_xShift = kdeEnergies.at(low->first)[0];
	_crossingAngle = kdeEnergies.at(low->first)[1];
	_axialRotation = kdeEnergies.at(low->first)[r];
	_zShift = kdeEnergies.at(low->first)[z];

	kdeReader.close();
}

// This one is for only angle and distance
void getGaussianKdeValues(Options &_opt, ofstream &_out, ofstream &_err){
	//Read Kde File
	Reader kdeReader(_opt.geometryDensityFile);
	kdeReader.open();
	map<double,vector<double>> kdeEnergies;

	if(!(kdeReader.is_open())){
		cerr << "WARNING: Unable to open " << _opt.geometryDensityFile << endl;
		exit(0);
	}

	vector<string> lines = kdeReader.getAllLines();

	//Break up kde file into lines
	for (int i=0; i<lines.size(); i++){
		vector<string> tokens = MslTools::tokenize(lines[i], "\t");
		if(tokens.size() < 1){
			continue;
		}
		if(tokens.size() != 3){
			_err << "WARNING: Line\"" << lines[i] << "\" is not in FORMAT: KDE(double) xShift(double) crossingAngle(double)";
			continue;
		}
		double kde = MslTools::toDouble(tokens[0]);

		vector<double> geometries;
		geometries.push_back(MslTools::toDouble(tokens[1]));
		geometries.push_back(MslTools::toDouble(tokens[2]));

		// Some kde values are duplicated. Don't want toi overwrite those, so setting this up to check if value is already in map. If so, add a 1 to the string so that it's a unique value
		map<double,vector<double>>::iterator itr;
		itr = kdeEnergies.find(kde);
		if (itr == kdeEnergies.end()){
			kdeEnergies[kde] = geometries;
		}
		else{
			kde = MslTools::toDouble(tokens[0]+"1");
			kdeEnergies[kde] = geometries;
		}
	}

	// Random Number Generator to randomly choose point in geometric space
	RandomNumberGenerator RNG;
	//TODO: for all spots with RNG, make sure you put options for using time based seed or not
	RNG.setSeed(MslTools::toInt(_opt.runNumber));
	
	auto it = kdeEnergies.begin();
	advance(it, RNG.getRandomInt(0,kdeEnergies.size()-1));
	
	double kdeValue = it->first;
	//cout << kdeEnergies.begin()->first << endl;
	//cout << kdeEnergies.end()->first << endl;
	//cout << kdeValue << endl;

	map<double,vector<double>>::iterator low;
	low = kdeEnergies.lower_bound(kdeValue);
	_out << "Found kde value: " << kdeValue << endl;
	cout << "Found kde value: " << kdeValue << endl;
	//double randKde = it->first;

	double xShift = kdeEnergies.at(kdeValue)[0];
	double crossingAngle = kdeEnergies.at(kdeValue)[1];

	while (xShift < 7.5 && crossingAngle < -25){
		it = kdeEnergies.begin();
		advance(it, RNG.getRandomInt(0,kdeEnergies.size()-1));
		//randKde = it->first;
		xShift = kdeEnergies.at(kdeValue)[0];
		crossingAngle = kdeEnergies.at(kdeValue)[1];
	}
	

	//map<double,vector<double>>::iterator low;
	//low = kdeEnergies.lower_bound(_kdeValue);
	//_out << "Found kde value: " << low->first << endl;

	//Set xShift and crossingAngle
	_opt.xShift = xShift;
	_opt.crossingAngle = crossingAngle;

	kdeReader.close();
}

// This one is for xShift, crossingAngle, zShift, and axialRotation
void getGaussianKdeValues(Options &_opt, string _geometryFile, vector<double> &_geoms, ofstream &_out, ofstream &_err){
	//Read Kde File
	Reader kdeReader(_geometryFile);
	kdeReader.open();
	map<double,vector<double>> kdeEnergies;

	if(!(kdeReader.is_open())){
		cerr << "WARNING: Unable to open " << _geometryFile << endl;
		exit(0);
	}

	vector<string> lines = kdeReader.getAllLines();
	//Break up kde file into lines
	for (int i=0; i<lines.size(); i++){
		vector<string> tokens = MslTools::tokenize(lines[i], "\t");
		if(tokens.size() < 1){
			continue;
		}
		if(tokens.size() != 3){
			_err << "WARNING: Line\"" << lines[i] << "\" is not in FORMAT: KDE(double) geom1(double) geom2(double)";
			continue;
		}
		double kde = MslTools::toDouble(tokens[0]);
		vector<double> geometries;
		geometries.push_back(MslTools::toDouble(tokens[1]));
		geometries.push_back(MslTools::toDouble(tokens[2]));

		// Some kde values are duplicated. Don't want toi overwrite those, so setting this up to check if value is already in map. If so, add a 1 to the string so that it's a unique value
		map<double,vector<double>>::iterator itr;
		itr = kdeEnergies.find(kde);
		if (itr == kdeEnergies.end()){
			kdeEnergies[kde] = geometries;
		}
		else{
			kde = MslTools::toDouble(tokens[0]+"1");
			kdeEnergies[kde] = geometries;
		}
	}

	// Random Number Generator to randomly choose point in geometric space
	RandomNumberGenerator RNG;
	//TODO: for all spots with RNG, make sure you put options for using time based seed or not
	RNG.setSeed(MslTools::toInt(_opt.runNumber));
	
	auto it = kdeEnergies.begin();
	advance(it, RNG.getRandomInt(0,kdeEnergies.size()-1));
	
	double kdeValue = it->first;

	map<double,vector<double>>::iterator low;
	low = kdeEnergies.lower_bound(kdeValue);
	_out << "Found kde value: " << kdeValue << endl;
	cout << "Found kde value: " << kdeValue << endl;

	_geoms.push_back(kdeEnergies.at(kdeValue)[0]);
	_geoms.push_back(kdeEnergies.at(kdeValue)[1]);
	
	kdeReader.close();
}

//TODO: add to a baseline file?
void buildPairInteractions(System &_sys, map<string,map<string,map<uint,double>>>& _pairMap){
	EnergySet* ESet = _sys.getEnergySet();
	for(uint i = 0; i < 2; i++) {
		Chain & thisChain = _sys.getChain(i);
		vector<Position*>& positions = thisChain.getPositions();
		for(vector<Position*>::iterator p = positions.begin(); p != positions.end(); p++){
			for (uint j=0; j < (*p)->identitySize(); j++){
				Residue &res1 = (*p)->getIdentity(j);
				string baseId1 = res1.getResidueName();
				if (p-positions.begin() < 4){
					baseId1 = baseId1.append("-ACE");
				}
				if (p-positions.begin() > positions.size()-5){//
					baseId1 = baseId1.append("-CT2");
				}
				//cout << "Identity " << j << ": " << baseId1 << endl;
				for (vector<Position*>::iterator p2 = p+1; p2 != positions.end(); p2++){
					uint d = p2-p;
					//cout << "Position 2: " << p2-positions.begin() << endl;
					if (d <= 10){
						//cout << "Distance: " << d << endl;
						for (uint k=0; k < (*p2)->identitySize(); k++){
							Residue &res2 = (*p2)->getIdentity(k);
							string baseId2 = res2.getResidueName();//TODO: check Charmm file top and par to see 
							if (p2-positions.begin() < 4){
								baseId2 = baseId2.append("-ACE");
							}
							if (p2-positions.begin() > positions.size()-5){//On 03_18_2021 I found this error; position.size() is weird, so need to use 5 instead of 4
								baseId2 = baseId2.append("-CT2");
							}
							try{
								map<string,map<uint,double>> AA1 = _pairMap.at(baseId1);
								map<uint,double> AA2 = AA1.at(baseId2);
								double ener = AA2.at(d);
								Atom *a = &res1.getAtom("CA");
								Atom *b = &res2.getAtom("CA");
								ESet->addInteraction(new BaselinePairInteraction(*a,*b,-1*ener));//I forgot that this needs to be the opposite sign to actually counteract the energies of vdW and hydrogen bonding; switched it here but should eventually just switch in my baseline parameter file
							}
							catch (const out_of_range& e){
								continue;		
							}
						}
					}
				}
			}
		}
	}
}//TODO: maybe try a getEnergy for a combo to see what the interaction is and if it's actually being saved?

void buildSelfInteractions(System &_sys, map<string, double> &_selfMap){
	EnergySet* ESet = _sys.getEnergySet();

	for(uint i = 0; i < 2; i++) {
		Chain & thisChain = _sys.getChain(i);
		vector<Position*>& positions = thisChain.getPositions();
		for(vector<Position*>::iterator p = positions.begin(); p != positions.end(); p++){
			for (uint j=0; j<(*p)->identitySize();j++){
				Residue &res = (*p)->getIdentity(j);
				string baseId = res.getResidueName();
				if (p-positions.begin() < 4 || p-positions.begin() > positions.size()-5){//On 03_18_2021 I found this error; position.size() is weird, so need to use 5 instead of 4
					baseId = baseId.append("-OUT");
				}
				try{
					double ener = _selfMap.at(baseId);
					Atom *a = &res.getAtom("CA");
					ESet->addInteraction(new BaselineInteraction(*a,ener));
				}
				catch (const out_of_range& e){
					continue;		
				}
			}
		}
	}
}

void buildSequenceEntropy(System &_sys, map<string, double> &_sequenceEntropyMap, double _weight){
	EnergySet* ESet = _sys.getEnergySet();

	for(uint i = 0; i < 1; i++) {
		Chain & thisChain = _sys.getChain(i);
		vector<Position*>& positions = thisChain.getPositions();
		//cout << "Chain: " << thisChain.toString() << endl;
		for(vector<Position*>::iterator p = positions.begin(); p != positions.end(); p++){
			//cout << "Position: " << p-positions.begin() << endl;
			for (uint j=0; j<(*p)->identitySize();j++){
				Residue &res = (*p)->getIdentity(j);//TODO: figure out if this is an error from 12_4_2020; if so, none of the runs were working for a reason...? changed it from i to j which I think it should be
				string baseId = res.getResidueName();
				//cout << "Identity " << j << ": " << baseId << endl;
				try{
					//cout << baseId << " worked" << endl;
					double ener = _sequenceEntropyMap.at(baseId);
					ener = -ener*(log2(ener))*_weight;
					//cout << "Energy: " << ener << endl;
					Atom *a = &res.getAtom("CA");
					ESet->addInteraction(new BaselineSequenceEntropy(*a,ener));
				}
				catch (const out_of_range& e){
					continue;
				}
			}
		}
	}
}

double baselineSelfEnergyOutput(System &_sys, map<string, double> &_selfMap){
	double totalEner = 0;

	for(uint i = 0; i < 1; i++) {
		Chain & thisChain = _sys.getChain(i);
		vector<Position*>& positions = thisChain.getPositions();

		for(vector<Position*>::iterator p = positions.begin(); p != positions.end(); p++){
			Residue &res = (*p)->getCurrentIdentity();
			string baseId = res.getResidueName();
			if (p-positions.begin() < 1){
				baseId = baseId.append("-ACE");
			}
			if (p-positions.begin() > positions.size()-2){
				baseId = baseId.append("-CT2");
			}
			try{
				double ener = _selfMap.at(baseId);
				totalEner = totalEner + ener;
			}
			catch (const out_of_range& e){
				continue;		
			}
		}
	}
	return totalEner;
}

double baselinePairEnergyOutput(System &_sys, map<string,map<string,map<uint,double>>>& _pairMap){
	double totalEner = 0;

	for(uint i = 0; i < 1; i++) {
		Chain & thisChain = _sys.getChain(i);
		vector<Position*>& positions = thisChain.getPositions();

		for(vector<Position*>::iterator p = positions.begin(); p != positions.end(); p++){
			Residue &res1 = (*p)->getCurrentIdentity();
			string baseId1 = res1.getResidueName();
			if (p-positions.begin() < 4){
				baseId1 = baseId1.append("-ACE");
			}
			if (p-positions.begin() > positions.size()-4){
				baseId1 = baseId1.append("-CT2");
			}
			for (vector<Position*>::iterator p2 = p+1; p2 != positions.end(); p2++){
				uint d = p2-p;
				if (d <= 10){
					Residue &res2 = (*p2)->getCurrentIdentity();
					string baseId2 = res2.getResidueName();
					if (p2-positions.begin() < 4){
						baseId2 = baseId2.append("-ACE");
					}
					if (p2-positions.begin() > positions.size()-4){
						baseId2 = baseId2.append("-CT2");
					}
					uint order = baseId1.compare(baseId2);
					if (order == 0){
						//cout << "Same AAs!" << endl;
						try{
							map<string,map<uint,double>> AA1 = _pairMap.at(baseId1);
							//cout << baseId1 << "worked" << endl;
							map<uint,double> AA2 = AA1.at(baseId1);
							//cout << baseId1 << "worked" << endl;
							double ener = -1*AA2.at(d);
							//cout << ener << "worked" << endl;
							totalEner = totalEner + ener;
						}
						catch (const out_of_range& e){
							continue;		
						}
					}
					else{
						//cout << "Different AAs!" << endl;
						set<string> sortAAs;
						sortAAs.insert(baseId1);
						sortAAs.insert(baseId2);
						vector<string> sort;
						for (set<string>::iterator s = sortAAs.begin(); s != sortAAs.end(); ++s){
							string a = *s;
							sort.push_back(a);
						}
						try{
							map<string,map<uint,double>> AA1 = _pairMap.at(sort[0]);
							//cout << sort[0] << "worked" << endl;
							map<uint,double> AA2 = AA1.at(sort[1]);
							//cout << sort[1] << "worked" << endl;
							double ener = -1*AA2.at(d);
							//cout << ener << "worked" << endl;
							totalEner = totalEner + ener;
						}
						catch (const out_of_range& e){
							continue;		
						}
					}
				}
			}
		}
	}
	return totalEner;
}

//hardcoded pair Baseline code that needs to be put into BaselineEnergyBuilder 
//The below are redacted and switched to readSingleParameter and readPairParameter
map<string, double> makeBaselineMap(string _file){
	map<string, double> m;
	vector<string> line;
	vector<string> AA;
	vector<double> ener;
	ifstream fs;
	fs.open(_file.c_str());
	if (!fs.is_open()){
		cerr << "Could not open baseline file" << endl;
	}
	else{
		string s;
		while(getline(fs, s)){
			istringstream iss(s);
			copy((istream_iterator<string>(iss)), istream_iterator<string>(), back_inserter(line));
		}
		fs.close();
	}
	//separate the input of each line into two separate vectors
	for (uint i=0; i<line.size(); i++){
		if (i % 2 == 0){
			AA.push_back(line[i]);
		}
		else{
			ener.push_back(MslTools::toDouble(line[i]));
		}
	}
	for (uint i=0; i<AA.size(); i++){
		m.insert(make_pair(AA[i], ener[i]));
	}

	return m;
}

map<string, vector<double>> makeBaselineMapPair(string _file){
	map<string, vector<double>> m;
	vector<string> line;
	vector<string> AA;
	vector<double> ener;
	ifstream fs;
	fs.open(_file.c_str());
	if (!fs.is_open()){
		cerr << "Could not open baseline file" << endl;
	}
	else{
		string s;
		while(getline(fs, s)){
			istringstream iss(s);
			copy((istream_iterator<string>(iss)), istream_iterator<string>(), back_inserter(line));
		}
		fs.close();
	}
	//separate the input of each line into two separate vectors
	for (uint i=0; i<line.size(); i++){
		if (i % 2 == 0){
			AA.push_back(line[i]);
		}
		else{
			ener.push_back(MslTools::toDouble(line[i]));
		}
	}
	
	string tmp;
	vector<double> es;
	for (uint i=0; i<AA.size(); i++){
		if  (i == 0){
			tmp = AA[i];
			es.push_back(ener[i]);
		}
		else{
			if (AA[i] == tmp){
				es.push_back(ener[i]);
			}
			else{
				m.insert({tmp, es});
				//reset the string and vector and push in the first value
				es.clear();
				tmp = AA[i];
				es.push_back(ener[i]);
			}
			if (i == AA.size()-1){
				m.insert({tmp, es});
				es.clear();
			}
		}
	}
	return m;
}

vector<vector<bool>> getRotamerMask(System &_sys, Options &_opt, vector<int> _variablePositions){
	vector<vector<bool>> mask;
	mask.resize(_opt.sequenceLength);
	for (uint i=0; i<_opt.sequenceLength; i++){
		//cout << 1 << endl;
		Position &pos = _sys.getPosition(i);
		int activeID = pos.getActiveIdentity();
		if (pos.identitySize() > 1){
		//cout << 3 << endl;
			vector<int> rotsToMask;
			vector<int> aliveRots;
			int totRots = pos.getTotalNumberOfRotamers();
			mask[i].resize(totRots);
			for (uint j=0; j<pos.identitySize(); j++){
		//cout << 4 << endl;
				int rots = pos.getTotalNumberOfRotamers(j);
				if (j<activeID){
					if (j==0){
						for(uint k=0; k<rots; k++){
							rotsToMask.push_back(k);
						}
					}
					else{
						int prevSize = rotsToMask.size();
						for(uint k=0; k<rots; k++){
							rotsToMask.push_back(k+prevSize);
						}
					}
				}
		//cout << 5 << endl;
				if (j==activeID){
					int prevSize = rotsToMask.size();
					for(uint k=0; k<rots; k++){
						aliveRots.push_back(k+prevSize);
					}
				}
				else{
					int prevSize = rotsToMask.size()+aliveRots.size();
					for(uint k=0; k<rots; k++){
						rotsToMask.push_back(k+prevSize);
					}
				}
			}
			for (uint k=0; k<rotsToMask.size(); k++){
				mask[i][rotsToMask[k]] = false;
			}
			for (uint k=0; k<aliveRots.size(); k++){
				mask[i][aliveRots[k]] = true;
			}
		}
		else{
		//cout << 2 << endl;
			int totRots = pos.getTotalNumberOfRotamers();
			mask[i].resize(totRots);
			for (uint j=0; j<totRots; j++){
				mask[i][j] = true;
			}
		}
	}
	return mask;
}

string randomPointMutation(System &_sys, Options &_opt, RandomNumberGenerator &_RNG, string &_seqToMutate, vector<int> _variablePositions, vector<string> _ids){
	// Get a random integer to pick through the variable positions
	int rand = _RNG.getRandomInt(0, _variablePositions.size()-1);
	int pos = _variablePositions[rand];

	// Get a random integer to pick through the AA identities
	int randIdNum = _RNG.getRandomInt(0, _ids.size()-1);
	string posId = _sys.getPosition(pos).getPositionId();
	string res = _sys.getPosition(pos).getResidueName();
	string randId;
	randId = _ids[randIdNum];

	string resOneL = MslTools::getOneLetterCode(randId.substr(0,3));//For some reason some of my AAs have spaces between them, likely because that's how the Msl getStringVector() reads it	
	//cout << "New Id: " << randId << " : " << resOneL << endl;

	string prevResID = MslTools::getOneLetterCode(res);
	//cout << "Old Id: " << res << " : " << prevResID << endl;
	//cout << prevResID << endl;

	// Write the mutated sequence
	string mutantSeq = "";
	for (uint i=0; i<_seqToMutate.length(); i++){
		if (i == pos){
			mutantSeq += resOneL;
		}
		else{
			mutantSeq += _seqToMutate[i];
		}
	}
	if (_opt.verbose){
		cout << prevResID << " at " << pos+_opt.thread << " switched to " << randId << endl;
		cout << "Previous seq: " << _seqToMutate << endl;
		cout << "Switched seq: " << mutantSeq << endl;
	}
	return mutantSeq;
}

void randomPointMutation(System &_sys, Options &_opt, RandomNumberGenerator &_RNG, vector<int> _variablePositions, vector<string> _ids, string &_prevPosId, string &_prevResId){
	// Get a random integer to pick through the variable positions
	int rand = _RNG.getRandomInt(0, _variablePositions.size()-1);
	int pos = _variablePositions[rand];

	// Get a random integer to pick through the AA identities
	int randIdNum = _RNG.getRandomInt(0, _ids.size()-1);
	string posId = _sys.getPosition(pos).getPositionId();
	_prevPosId = posId;
	string randId;
	randId = _ids[randIdNum];

	string res = _sys.getPosition(pos).getResidueName();
	_prevResId = res;
	
	_sys.setActiveIdentity(posId, randId);
}

//based off of random point mutation: gets a random position and chooses a random rotamer
void randomRotamerChange(System &_sys, Options &_opt, RandomNumberGenerator &_RNG, vector<int> _variablePositions, vector<unsigned int> &_stateVec){
	// Get a random integer to pick through the variable positions
	int rand = _RNG.getRandomInt(0, _variablePositions.size()-1);
	int pos = _variablePositions[rand];

	// Get the random position from the system
	Position &randPos = _sys.getPosition(pos);
	string posId = randPos.getPositionId();
	int numRots = randPos.getTotalNumberOfRotamers();
	
	// Get a random integer to pick the rotamer
	int randRot = _RNG.getRandomInt(0, numRots-1);
	_stateVec[pos] = randRot;
	randPos.setActiveRotamer(randRot);
}

//while loop to reset the sequence and make another mutation
void resetAndSwitchSequence(System &_sys, Options &_opt, RandomNumberGenerator &_RNG, vector<int> _variablePositions, vector<string> _ids, string &_prevPosId, string &_prevResId, string &_currSeq, vector<string> &_allSeqs, bool &_sameSeq){
	int c = 0;
	while (_sameSeq == true){
		_sys.setActiveIdentity(_prevPosId, _prevResId);
		randomPointMutation(_sys, _opt, _RNG, _variablePositions, _ids, _prevPosId, _prevResId);
		_sameSeq = sameSequenceChecker(_currSeq, _allSeqs);
		c++;
		if (c > 1000){//It has gotten stuck on a sequence that switching to any AA
			_sameSeq = false;
		}
	}
}

map<string,int> getAACountMap(vector<string> _seq){
	map<string,int> AAcounts;
	for (uint i=0; i<_seq.size(); i++){
		try{
			if (AAcounts.count(_seq[i]) > 0){
				AAcounts.at(_seq[i])++;
			}
			else{
				AAcounts[_seq[i]] = 1;
			}
		}
		catch(const out_of_range& e){
			continue;
		}
	}
	return AAcounts;
}

double calcNumberOfPermutations(map<string,int> _seqAACounts, int _seqLength){
	//This function calculates number of permutations using following equation: n!/(n-r)! where n is number of positions and r is number of AAs	
	double numPermutation = 1;
	double permutationDenominator = 1;
	for(uint i=_seqLength; i>1; i--){
		numPermutation = numPermutation*i;
	}
	map<string,int>::iterator itr;
	for(itr = _seqAACounts.begin(); itr != _seqAACounts.end(); itr++){
		for (uint j=itr->second; j>1; j--){
			permutationDenominator = permutationDenominator*j;
		}
	}
	numPermutation = numPermutation/permutationDenominator;
	return numPermutation;
}

void sequenceEntropySetup(string _seq, map<string,int> &_seqCountMap, double &_numberOfPermutations, int _seqLength){
	vector<string> seqVector;
	for (uint i=0; i<_seq.length(); i++){
		stringstream tmp;
		tmp << _seq[i];
		string aa = tmp.str();
		string resName = MslTools::getThreeLetterCode(aa);
		seqVector.push_back(resName);
	}
	_seqCountMap = getAACountMap(seqVector);
	_numberOfPermutations = calcNumberOfPermutations(_seqCountMap, _seqLength);
}

double calculateSequenceProbability(map<string,int> &_seqCountMap, map<string,double> &_entropyMap, double _numberOfPermutations){
	//Find AA in count map, get counts of AA, then calculate the sequence probability by multiplying each AAs membrane probability contribution
	double seqProb = 1;
	map<string,int>::iterator it;
	for (it=_seqCountMap.begin(); it != _seqCountMap.end(); it++){
		double memProb = _entropyMap.at(it->first);
		int count = it->second;
		seqProb = seqProb*(pow(memProb, count));
	}
	seqProb = seqProb*_numberOfPermutations;
	return seqProb;
}

//TODO: maybe just read the sequence entropy map here? 
void calculateSequenceEntropy(Options &_opt, string _prevSeq, string _currSeq, map<string,double> _entropyMap, double &_prevSEProb, double &_currSEProb, double _bestEnergy, double _currEnergy, double &_bestEnergyTotal, double &_currEnergyTotal){
	map<string,int> prevSeqCountMap;
	map<string,int> currSeqCountMap;
	double currNumberOfPermutations;
	double prevNumberOfPermutations;
	
	//Calculate the sequence entropy for both sequences
	sequenceEntropySetup(_prevSeq, prevSeqCountMap, prevNumberOfPermutations, _opt.sequenceLength);
	sequenceEntropySetup(_currSeq, currSeqCountMap, currNumberOfPermutations, _opt.sequenceLength);
	_prevSEProb = calculateSequenceProbability(prevSeqCountMap, _entropyMap, prevNumberOfPermutations);
	_currSEProb = calculateSequenceProbability(currSeqCountMap, _entropyMap, currNumberOfPermutations);

	//Calculate the probability of each sequence compared to the other
	double totSEProb = _prevSEProb+_currSEProb;
	double prevSeqProp = _prevSEProb/totSEProb;
	double currSeqProp = _currSEProb/totSEProb;

	//Convert the probability of each sequence to an entropy term that can be added to the original energy to directly compare two sequences
	double prevEner = -log(prevSeqProp)*0.592*_opt.weight_seqEntropy;//Multiplies the energy (log proportion times RT in kcal/mol) by the sequence entropy weight (weight of 1 gives entropy same weight as other terms)
	double currEner = -log(currSeqProp)*0.592*_opt.weight_seqEntropy;
	
	//Calculate energy total for best sequence vs current sequence
	//The below includes the baseline energy, which is an estimate of monomer energy
	_bestEnergyTotal = _bestEnergy+prevEner;
	_currEnergyTotal = _currEnergy+currEner;//TODO: I would like to include these in analysis somehow, but can't thikn of a way to do so

	//Output the terms if verbose
	if (_opt.verbose){
		cout << "Prev Prob:    " << _prevSEProb << endl;
		cout << "New Prob:     " << _currSEProb << endl;
		cout << "Prev Seq Proportion: " << prevSeqProp << endl;
		cout << "New Seq Proportion:  " << currSeqProp << endl;
		cout << "PrevEner =    " << prevEner << endl;
		cout << "NewEner =     " << currEner << endl;
		cout << "Diff =        " << (prevEner-currEner) << endl;
		cout << "Best Energy: " << _bestEnergyTotal << endl;
		cout << "New Energy: " << _currEnergyTotal << endl;
	}
}

//Now I just need to put limits on their sizes
void saveSequence(Options &_opt, vector<vector<pair<double,string>>> &_energyVectors, string _sequence, double _energy){
	for (uint i=1; i<_energyVectors.size(); i++){
		if (_energy < _opt.energyLimit){
			if (_energyVectors[0].size() < _opt.numStatesToSave/_opt.numberEnergyVectors){
				_energyVectors[0].push_back(make_pair(_energy, _sequence));
			}
			else{
				sort(_energyVectors[0].begin(), _energyVectors[0].end());
				if (_energyVectors[0][0].first > _energy){
					_energyVectors[0][0].first = _energy;
					_energyVectors[0][0].second = _sequence;
				}
			}
			i = _energyVectors.size();
		}
		else{
			if (_energy > _opt.energyLimit+(_opt.energyDifference*i) && _energy < _opt.energyLimit+(_opt.energyDifference*(i+1))){
				if (_energyVectors[i].size() < _opt.numStatesToSave/_opt.numberEnergyVectors){
					_energyVectors[i].push_back(make_pair(_energy, _sequence));
				}
				else{
					sort(_energyVectors[i].begin(), _energyVectors[i].end());
					if (_energyVectors[i][0].first > _energy){
						_energyVectors[i][0].first = _energy;
						_energyVectors[i][0].second = _sequence;
					}
				}
				i = _energyVectors.size();
			}
		}
	}
}

void stateMC(System &_sys, Options &_opt, Transforms &_trans, map<string, map<string,double>> &_seqEnergyMap, map<vector<unsigned int>, map<string,double>> &_stateEnergyMap, SelfPairManager &_spm, vector<unsigned int> _bestState, vector<string> &_seqs, vector<string> &_allSeqs, vector<pair<string,vector<uint>>> &_seqStatePair, vector<int> &_variableInterfacialPositionsList, vector<int> &_allInterfacialPositions, RandomNumberGenerator &_RNG, map<string, double> _selfMap, map<string, double> _seqEntMap, map<string,map<string,map<uint, double>>> _pairMap, ofstream &_sout, ofstream &_err){

	time_t startTimeSMC, endTimeSMC;
	double diffTimeSMC;
	time(&startTimeSMC);
	
	// Setup MonteCarloManager
	MonteCarloManager MC(_opt.MCStartTemp, _opt.MCEndTemp, _opt.MCCycles, _opt.MCCurve, 50);
	MC.setRandomNumberGenerator(&_RNG);

	Chain & chain = _sys.getChain("A");

	// Start from most probable state
	_sys.setActiveRotamers(_bestState);
	double bestEnergy = _spm.getStateEnergy(_bestState);

	// State variable setup
	vector<unsigned int> prevStateVec = _bestState;
	vector<unsigned int> currStateVec = _bestState;
	MC.setEner(bestEnergy);
	
	// initialize map for accepting energies
	map<string,double> stateMCEnergies;

	// initialize energy variables for the MonteCarlo
	double prevStateSEProb = 0;
	double totEnergy = 0;

	// Alternate AA Ids for each of the interfacial positions
	vector<string> ids = _opt.Ids;
	ids.push_back("LEU");

	// Variables setup for MC while loop
	map<double, string> sequences;
	int cycleCounter = 0;
	string prevStateSeq = convertPolymerSeqToOneLetterSeq(chain);

	// initialize energy vectors
	vector<vector<pair<double,string>>> energyVectors;
	for (uint i=0; i<_opt.numberEnergyVectors; i++){
		vector<pair<double,string>> eV;
		energyVectors.push_back(eV);
	}

	// Setup EnergyLandscape file
	ofstream lout;
	string loutfile  = _opt.pdbOutputDir + "/stateMCEnergyLandscape.out";
	lout.open(loutfile.c_str());
	lout << "***STARTING GEOMETRY:***" << endl;
	lout << "xShift: " << _opt.xShift << endl;
	lout << "crossingAngle: " << _opt.crossingAngle << endl;
	lout << "axialRotation: " << _opt.axialRotation << endl;
	lout << "zShift: " << _opt.zShift << endl << endl;
	lout << "Number of MCCycles: " << _opt.MCCycles << endl;
	lout << "Design Number\tTotal Cycles\tSequence\tTotal\tDimer\tBaseline\tVDWDimer\tHBONDDimer\tEnergyw/seqEntropy\tCycle" << endl;

	// Setup PDB writer
	//PDBWriter designWriter;
	//designWriter.open(_opt.pdbOutputDir + "/enerLandscapesDesigns.pdb");

	// Begin MonteCarlo sequence optimization loop
	while (!MC.getComplete()){
		if (_opt.verbose){
			cout << "Cycle #" << cycleCounter << "" << endl;
			cout << "Starting Seq: " << prevStateSeq << endl;
		}
		
		// Get energy term and probability for the first sequence (these terms can then get replaced by future sequences that are accepted by MC)
		if (cycleCounter == 0){
			outputEnergiesByTerm(_spm, prevStateVec, stateMCEnergies, _opt.energyTermList, "DimerNoIMM1", 0);
			bestEnergy = bestEnergy-stateMCEnergies["Baseline"];
			stateMCEnergies["DimerNoIMM1"] = bestEnergy;
		
			_stateEnergyMap[prevStateVec] = stateMCEnergies;
			totEnergy = stateMCEnergies["EnergyBeforeLocalMC"];
			sequences[totEnergy] = prevStateSeq;
			saveSequence(_opt, energyVectors, prevStateSeq, totEnergy);
		}
		// Reset the energy map to save energies from new state after changing the rotamer
		stateMCEnergies.clear();
		randomRotamerChange(_sys, _opt, _RNG, _variableInterfacialPositionsList, currStateVec);
		
		// Get the sequence for the random state
		string currStateSeq = convertPolymerSeqToOneLetterSeq(chain);
		
		// Compute dimer energy
		outputEnergiesByTerm(_spm, currStateVec, stateMCEnergies, _opt.energyTermList, "DimerNoIMM1", 0);
		double currStateEnergy = _spm.getStateEnergy(currStateVec);
		stateMCEnergies["DimerNoIMM1"] = currStateEnergy;
		
		// Convert the energy term (which actually saves the probability of the sequence in the whole system)
		// to the proper comparison of proportion to energy between individual sequences (done outside of the actual energy term)
		double bestEnergyTotal;
		double currEnergyTotal;
		double currStateSEProb;
		calculateSequenceEntropy(_opt, prevStateSeq, currStateSeq, _seqEntMap, prevStateSEProb, currStateSEProb, bestEnergy, currStateEnergy, bestEnergyTotal, currEnergyTotal);
		MC.setEner(bestEnergyTotal);

		// MC accept and reject conditions
		if (!MC.accept(currEnergyTotal)){
			_sys.setActiveRotamers(prevStateVec);
			currStateVec = prevStateVec;

			if (_opt.verbose){
				cout << "State not accepted, E= " << currEnergyTotal << "; PrevE= " << bestEnergyTotal << endl << endl;
			}
		} else {
			saveSequence(_opt, energyVectors, currStateSeq, currStateEnergy);
			bestEnergy = currStateEnergy;
			MC.setEner(currEnergyTotal);
			prevStateSEProb = currStateSEProb;
			prevStateSeq = currStateSeq;
			//prevStateMonomerEnergy = currStateMonomerEnergy;
			prevStateVec = currStateVec;
			_sys.setActiveRotamers(currStateVec);
			stateMCEnergies["EnergyBeforeLocalMC"] = currStateEnergy;
			stateMCEnergies["EnergyBeforeLocalMCw/seqEntropy"] = bestEnergyTotal-currEnergyTotal;
			_stateEnergyMap[currStateVec] = stateMCEnergies;

			if (_opt.energyLandscape){
				map<string,double> energyMap = _stateEnergyMap.at(currStateVec);
				//TODO: figure out a way to output the state changes/decide if that's a good idea
				lout << "State: ";
				for (uint j=0; j<currStateVec.size(); j++){
					if (j!=currStateVec.size()-1){
						lout << currStateVec[j] << ",";
					}
					else{
						lout << currStateVec[j] << endl;
					}
				}
				lout << _opt.runNumber << "\t" << _opt.MCCycles << "\t" << currStateSeq << "\t";
				cout << currStateSeq << "\t";
				for (uint j=0; j<_opt.enerLandscapeTerms.size(); j++){
					cout << _opt.enerLandscapeTerms[j] << endl;
					lout << energyMap.at(_opt.enerLandscapeTerms[j]) << "\t";
					cout << energyMap.at(_opt.enerLandscapeTerms[j]) << "\t";
				}
				lout << cycleCounter << endl;
				cout << endl;
				//designWriter.write(_sys.getAtomPointers(), true, false, true);
			}

			if (_opt.verbose) {
				 cout << "Cycle#" << cycleCounter << " State accepted, Sequence: " << currStateSeq << "; PrevE=  " << bestEnergyTotal << " : MCEner= " << currEnergyTotal << endl << endl;
				_sout << "Cycle#" << cycleCounter << " State accepted, Sequence: " << currStateSeq << "; PrevE=  " << bestEnergyTotal << " : MCEner= " << currEnergyTotal << endl << endl;
			}
		}
		if (MC.getComplete() == true && MC.getCurrentT() < 546.4){
			MC.reset(3649, 3649, 100, MonteCarloManager::EXPONENTIAL, 10);//Approximately 50% likely to accept within 5kcal, and 25% likely to accept within 10kcal
			//MC.reset(100000, 100000, 1000, MonteCarloManager::EXPONENTIAL, 10);
			cout << "MonteCarlo Reset!" << endl;
			for (uint i=0; i<energyVectors.size(); i++){
				for (uint j=0; j<energyVectors[i].size(); j++){
					cout << i << ", " << j << ": " << energyVectors[i][j].first << " " << energyVectors[i][j].second << endl;
					//bool sameseq = sameSequenceChecker(energyVectors[i][j].second, _allSeqs);
				}
			}
		}
		cycleCounter++;
	}
	time(&endTimeSMC);
	diffTimeSMC = difftime (endTimeSMC, startTimeSMC);

	lout << "Time: " << diffTimeSMC << "s" << endl;
	//designWriter.close();
	_allSeqs.clear();
	for (uint i=0; i<energyVectors.size(); i++){
		for (uint j=0; j<energyVectors[i].size(); j++){
			cout << i << ", " << j << ": " << energyVectors[i][j].first << " " << energyVectors[i][j].second << endl;
			bool sameseq = sameSequenceChecker(energyVectors[i][j].second, _allSeqs);
		}
	}

	//convert stateEnergyMap to seqEnergyMap
	map<vector<uint>,map<string,double>>::iterator itr;
//TODO: The state is not always correct: I am getting different vdW energies. I need to make sure I'm getting the proper state from the energy map
	for (itr = _stateEnergyMap.begin(); itr != _stateEnergyMap.end(); itr++){
		vector<uint> state = itr->first;
		_sys.setActiveRotamers(state);
		string currSeq = convertPolymerSeqToOneLetterSeq(chain);
		if (find(_allSeqs.begin(), _allSeqs.end(), currSeq) != _allSeqs.end()){//see if occurs in sequence vector and in map
			map<string, double> energyMap = itr->second;
			map<string,map<string,double>>::iterator itrf;
			itrf = _seqEnergyMap.find(currSeq);
			if (itrf == _seqEnergyMap.end()){
				_seqEnergyMap[currSeq] = energyMap;
				_seqStatePair.push_back(make_pair(currSeq, state));
			}
			else if (energyMap.at("DimerNoIMM1") < _seqEnergyMap.at(currSeq).at("DimerNoIMM1")){
//This pair thing is kind of a headache? Maybe I should just switch it to a map if I don't figure it out easily
				vector<pair<string,vector<uint>>>::iterator itrPair;
				for (itrPair = _seqStatePair.begin(); itrPair != _seqStatePair.end(); itrPair++){
					if (itrPair->first == currSeq){
						_seqStatePair.erase(itrPair);
						_seqEnergyMap[currSeq] = energyMap;
						_seqStatePair.push_back(make_pair(currSeq, state));
					}
				}
			}
		}
	}
	for (uint i=0; i<_seqStatePair.size(); i++){
		cout << _seqStatePair[i].first << "; ";
		for (uint j=0; j<_seqStatePair[i].second.size(); j++){
			cout << _seqStatePair[i].second[j] << ", ";
		}
		cout << endl;
		cout << _seqStatePair[i].first << ": " << _spm.getStateInteractionCount(_seqStatePair[i].second, "CHARMM_VDW") << endl;
		cout << _spm.getSummary(_seqStatePair[i].second) << endl;


	}
	if (_opt.verbose){
		//cout << "Best Energy: " << bestEnergy << endl;
		cout << "#Seqs: " << _allSeqs.size() << endl;
		cout << "SMC Time: " << diffTimeSMC << "s" << endl;
		_sout << "#Seqs: " << _allSeqs.size() << endl;
		_sout << "SMC Time: " << diffTimeSMC << "s" << endl << endl;
	}
	lout.close();
//exit(0);
	//map<double,string>::iterator itr;
	//for (itr=sequences.begin(); itr!=sequences.end(); itr++){
	//	bool sameseq = sameSequenceChecker(itr->second, _allSeqs);
	//}
}

//TODO: may need to add a scan in to find the best zShift for the dimer
void calculateDimerEnergies(System &_sys, PolymerSequence &_PL, Options &_opt, vector<string> &_seqs, vector<pair<string,vector<uint>>> &_seqStatePair, map<string,map<string,double>> &_seqEnergyMap, vector<double> &_monomerEnergies, vector<double> &_dimerEnergies, vector<double> &_finalEnergies, vector<int> &_allInterfacialPositions, vector<vector<string>> &_linkedPos, ofstream &_sout, PDBWriter &_writer){
	
	System sysDimer;
	CharmmSystemBuilder CSBDimer(sysDimer,_opt.topFile,_opt.parFile,_opt.solvFile);
	CSBDimer.setBuildTerm("CHARMM_ELEC", false);
	CSBDimer.setBuildTerm("CHARMM_ANGL", false);
	CSBDimer.setBuildTerm("CHARMM_BOND", false);
	CSBDimer.setBuildTerm("CHARMM_DIHE", false);
	CSBDimer.setBuildTerm("CHARMM_IMPR", false);
	CSBDimer.setBuildTerm("CHARMM_U-BR", false);
	CSBDimer.setBuildTerm("CHARMM_IMM1REF", true);
	CSBDimer.setBuildTerm("CHARMM_IMM1", true);
	
	CSBDimer.setSolvent("MEMBRANE");
	CSBDimer.setIMM1Params(15, 10);
	
	CSBDimer.setBuildNonBondedInteractions(false);
	if(!CSBDimer.buildSystem(_PL)) {
		cerr << "Unable to build system from " << _PL << endl;
		exit(0);
	}
	
	/******************************************************************************
	 *           === TRANSFORM HELICES TO INITIAL STARTING POSITION ===
	 ******************************************************************************/
	sysDimer.assignCoordinates(_sys.getAtomPointers(),false);
	sysDimer.buildAllAtoms();
	
	SystemRotamerLoader sysDimerRot(sysDimer, _opt.rotLibFile);
	sysDimerRot.defineRotamerSamplingLevels();
	
	// Add hydrogen bond term
	HydrogenBondBuilder hb(sysDimer, _opt.hBondFile);
	hb.buildInteractions(50);//when this is here, the HB weight is correct
	
	/******************************************************************************
	 *                     === INITIAL VARIABLE SET UP ===
	 ******************************************************************************/
	EnergySet* EsetDimer = sysDimer.getEnergySet();
	// Set all terms active, besides Charmm-Elec
	EsetDimer->setAllTermsActive();
	EsetDimer->setTermActive("CHARMM_ELEC", false);
	EsetDimer->setTermActive("CHARMM_ANGL", false);
	EsetDimer->setTermActive("CHARMM_BOND", false);
	EsetDimer->setTermActive("CHARMM_DIHE", false);
	EsetDimer->setTermActive("CHARMM_IMPR", false);
	EsetDimer->setTermActive("CHARMM_U-BR", false);
	EsetDimer->setTermActive("CHARMM_IMM1", true);
	EsetDimer->setTermActive("CHARMM_IMM1REF", true);
	EsetDimer->setTermActive("SCWRL4_HBOND", true);
	
	/******************************************************************************
	 *             === SETUP ENERGY SET FOR MONOMER COMPARISON ===
	 ******************************************************************************/
	EsetDimer->setWeight("CHARMM_VDW", 1);
	EsetDimer->setWeight("SCWRL4_HBOND", 1);
	EsetDimer->setWeight("CHARMM_IMM1", 1);
	EsetDimer->setWeight("CHARMM_IMM1REF", 1);
	
	/******************************************************************************
	 *                === DELETE TERMINAL HYDROGEN BOND INTERACTIONS ===
	 ******************************************************************************/
	deleteTerminalHydrogenBondInteractions(sysDimer,_opt);
	
	/******************************************************************************
	 *                  === GREEDY TO OPTIMIZE ROTAMERS ===
	 ******************************************************************************/
	//Random Number Generator/
	RandomNumberGenerator RNG;
	//RNG.setSeed(_opt.seed); 
	RNG.setTimeBasedSeed();
	
	CSBDimer.updateNonBonded(10,12,50);
	sysDimer.buildAllAtoms();
	
	sysDimer.setLinkedPositions(_linkedPos);
	
	loadRotamers(sysDimer, sysDimerRot, _opt.SL);
	loadInterfacialRotamers(sysDimer, sysDimerRot, _opt.SLInterface, _allInterfacialPositions);
	
	CSBDimer.updateNonBonded();
	sysDimer.buildAllAtoms();
	
	// Optimize Initial Starting Position (using Baseline to get back to original result)
	SelfPairManager spmDimer;
	spmDimer.seed(RNG.getSeed());
	spmDimer.setSystem(&sysDimer);
	spmDimer.setVerbose(false);
	spmDimer.getMinStates()[0];
	spmDimer.updateWeights();
	spmDimer.setOnTheFly(true);
	spmDimer.saveEnergiesByTerm(true);
	spmDimer.calculateEnergies();
	
	//spmTime = difftime (spmEnd, spmStart);
	_sout << "***CALCULATE DIMER ENERGY WITHOUT LOCAL REPACK***" << endl << endl;
cout << _seqStatePair.size() << endl;
	for(uint i=0; i<_seqStatePair.size(); i++){
		string sequence = _seqStatePair[i].first;
		vector<uint> stateVec = _seqStatePair[i].second;
		sysDimer.setActiveRotamers(stateVec);

		//Calculate Dimer energy for output
		double dimerEnergy = spmDimer.getStateEnergy(stateVec);
		double finalEnergy = dimerEnergy-_seqEnergyMap[sequence]["Monomer"];//TODO: make this more elegant by pulling from the map 
		_sout << "Dimer Energy: " << dimerEnergy << endl << endl;
	
		cout << sequence << ": " << spmDimer.getStateInteractionCount(stateVec, "CHARMM_VDW") << endl;
		cout << spmDimer.getSummary(stateVec) << endl;
		map<string,double> &energyMap = _seqEnergyMap[sequence];
		outputEnergiesByTerm(spmDimer, stateVec, energyMap, _opt.energyTermList, "Dimer", 1);
		//TODO: need to eventually just rid of this distinction: output a normal file AND an energy landscape file
		if (!_opt.energyLandscape){
			double imm1 = EsetDimer->getTermEnergy("CHARMM_IMM1REF")+EsetDimer->getTermEnergy("CHARMM_IMM1");
			for (uint i=0; i<_opt.energyTermList.size(); i++){
				if (_opt.energyTermList[i] == "CHARMM_IMM1REF" || _opt.energyTermList[i] == "CHARMM_IMM1"){
					_seqEnergyMap[sequence]["IMM1Dimer"] = imm1;
				}
				else{
					string energyTerm = _opt.energyTermList[i];
					string energyLabel = energyTerm.substr(7,energyTerm.length())+"Dimer";
					_seqEnergyMap[sequence][energyLabel] = EsetDimer->getTermEnergy(_opt.energyTermList[i]);
				}
			}
			_seqEnergyMap[sequence]["Dimer"] = dimerEnergy;
			_seqEnergyMap[sequence]["Total"] = finalEnergy;
			
			//Write PDB
			PDBWriter designWriter;
			designWriter.open(_opt.pdbOutputDir + "/design_" + MslTools::intToString(i) + ".pdb");
			designWriter.write(sysDimer.getAtomPointers(), true, false, true);
			_writer.write(sysDimer.getAtomPointers(), true, false, true);
			designWriter.close();
			saveEnergyDifference(_opt, _seqEnergyMap, sequence);
		}
		else{
			_seqEnergyMap[sequence]["Dimer"] = dimerEnergy;
			_seqEnergyMap[sequence]["Total"] = finalEnergy;
			_finalEnergies.push_back(finalEnergy);
			_dimerEnergies.push_back(dimerEnergy);
			PDBWriter designWriter;
			designWriter.open(_opt.pdbOutputDir + "/design_" + MslTools::intToString(i) + ".pdb");
			designWriter.write(sysDimer.getAtomPointers(), true, false, true);
			_writer.write(sysDimer.getAtomPointers(), true, false, true);
			designWriter.close();
			saveEnergyDifference(_opt, _seqEnergyMap, sequence);
		}
	}
}

/******************************************
 *  
 *  =======  BEGIN MAIN =======
 *
 ******************************************/
int main(int argc, char *argv[]){

	//TODO: add in ways to fix my code so that I don't output as many things to save time
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
	Options opt = parseOptions(argc, argv, defaults);
	
	if (opt.errorFlag) {
		cerr << endl;
		cerr << "The program terminated with errors:" << endl;
		cerr << endl;
		cerr << opt.errorMessages << endl;
		cerr << endl;
		cerr << opt.OPerrors << endl;

		usage();
		exit(1);
	}

	/******************************************************************************
	 *                       === SETUP OUTPUT FILES ===
	 ******************************************************************************/
	ofstream sout;
	ofstream err;

	opt.pdbOutputDir = opt.pdbOutputDir + "/" + date;
	string cmd = "mkdir -p " + opt.pdbOutputDir;
	if (system(cmd.c_str())){
		cout << "Unable to make directory" << endl;
		exit(0);
	}
	opt.pdbOutputDir = opt.pdbOutputDir + "/design_" + opt.runNumber;
	cmd = "mkdir -p " + opt.pdbOutputDir;

	if (system(cmd.c_str())){
		cout << "Unable to make directory" << endl;
		exit(0);
	}

	string soutfile = opt.pdbOutputDir + "/summary.out";
	string errfile  = opt.pdbOutputDir + "/errors.out";

	sout.open(soutfile.c_str());
	err.open(errfile.c_str());

	sout << date << endl;
	err << date << endl;

	//TODO: add config file output
	//printOptions(opt, pout);
	
	if (opt.errorFlag) {
		err << endl;
		err << "The program terminated with errors:" << endl;
		err << endl;
		err << opt.errorMessages << endl;
		err << endl;
		err << opt.OPerrors << endl;

		usage();
		exit(1);
	}
	
	/******************************************************************************
	 *   === CHOOSE XSHIFT AND CROSSING ANGLE FROM DISTRIBUTION OF PDB DATA ===
	 ******************************************************************************/
	RandomNumberGenerator geoRNG;
	geoRNG.setSeed(MslTools::toInt(opt.runNumber));
	
	// Values for bin size of each geometry: helps to make the code explore the entire geometric space rather than fixed bin points (TODO: calculate in the future)
	double crossingAngleBinDiff = 5.128205;
	double xShiftBinDiff = 0.26087;
	double axialRotBinDiff = 5.263158;
	double zShiftBinDiff = 0.315789;
	if (opt.useGeoFromPDBData){
		//TODO: automate this so that if I decide to use different kdes I can just plug the file in (need it to add everything in the file together and calculate these)
		double ad_normSD = 0.00107102*3;
		double ad_normMean = 0.001041667;
	
		double ad_randNorm = geoRNG.getRandomDouble(0,1);//This is good in principle, but it's usually giving large values...how do I get it to be more likely to give small values?
		cout << ad_randNorm << endl;
		ad_randNorm = (ad_randNorm*ad_normSD)+ad_normMean;
		cout << "Rand Norm " << ": " << ad_randNorm << endl;
		
		// Setup output files
		//ofstream gkout;
		//string gkoutfile = opt.pdbOutputDir+"/gaussian_kde_values.out";
		//gkout.open(gkoutfile.c_str());
		//gkout << "Randomly chosen kde values: xShift: Angle: Rot: Z" << endl;
		//gkout << "Random Kde Values:	" << ad_randNorm << endl;

		//TODO: put all of this data into one file
		// Get xShift and crossingAngle 
		getGaussianKdeValues(opt, sout, err);

		// Get zShift
		vector<double> geoms;
		getGaussianKdeValues(opt, "/exports/home/gloiseau/mslib/trunk_AS/myProgs/gloiseau/2021_05_28_20cutoff_zkde.txt", geoms, sout, err);
		double rand = geoRNG.getRandomInt(0,1);
		opt.zShift = geoms[rand];
		geoms.clear();

		// Get axialRotation
		getGaussianKdeValues(opt, "/exports/home/gloiseau/mslib/trunk_AS/myProgs/gloiseau/2021_05_28_20cutoff_rotkde.txt", geoms, sout, err);
		opt.axialRotation = geoms[rand];
		rand = geoRNG.getRandomInt(0,1);

		// Choose a random point within the given geometric bins
		opt.xShift = opt.xShift + geoRNG.getRandomDouble(-xShiftBinDiff, xShiftBinDiff);
		opt.crossingAngle = opt.crossingAngle + geoRNG.getRandomDouble(-crossingAngleBinDiff, crossingAngleBinDiff);
		opt.axialRotation = opt.axialRotation + geoRNG.getRandomDouble(-axialRotBinDiff, axialRotBinDiff);
		opt.zShift = opt.zShift + geoRNG.getRandomDouble(-zShiftBinDiff, zShiftBinDiff);

		//gkout << "Geometry:	" << opt.xShift << "	" << opt.crossingAngle << "	" << opt.axialRotation << "	" << opt.zShift << endl;
		//gkout.close();
	}
	
	/******************************************************************************
	 *                        === SETUP SUMMARY FILE ===
	 ******************************************************************************/
	cout  << "***STARTING GEOMETRY:***" << endl;
	cout  << "xShift: " << opt.xShift << endl;
	cout  << "crossingAngle: " << opt.crossingAngle << endl;
	cout  << "axialRotation: " << opt.axialRotation << endl;
	cout  << "zShift: " << opt.zShift << endl << endl;
	sout << "***STARTING GEOMETRY:***" << endl;
	sout << "xShift: " << opt.xShift << endl;
	sout << "crossingAngle: " << opt.crossingAngle << endl;
	sout << "axialRotation: " << opt.axialRotation << endl;
	sout << "zShift: " << opt.zShift << endl << endl;
	
	/******************************************************************************
	 *                         === GENERATE POLYGLY ===
	 ******************************************************************************/
	string polyGly = generatePolymerSequence("A", opt.sequenceLength, opt.thread);
	PolymerSequence PS(polyGly);

//TODO: change this part to make more simple (only need one system to get the interface and to translate rather than translating to another spot)
	/******************************************************************************
	 *                     === DECLARE SYSTEM ===
	 ******************************************************************************/
	System sys;
	CharmmSystemBuilder CSB(sys,opt.topFile,opt.parFile);
	CSB.setBuildNoTerms();
	
	if(!CSB.buildSystem(PS)) {
		err << "Unable to build system from " << polyGly << endl;
		exit(0);
	}

	Chain & chainA = sys.getChain("A");
	Chain & chainB = sys.getChain("B");

	// Set up chain A and chain B atom pointer vectors
	AtomPointerVector & apvChainA = chainA.getAtomPointers();
	AtomPointerVector & apvChainB = chainB.getAtomPointers();

	/******************************************************************************
	 *                     === COPY BACKBONE COORDINATES ===
	 ******************************************************************************/
	System pdb;
	pdb.readPdb(opt.infile);//gly69 pdb file; changed from the CRD file during testing to fix a bug but both work and the bug was separate
	
	sys.wipeAllCoordinates();
	sys.assignCoordinates(pdb.getAtomPointers(),false);
	sys.buildAllAtoms();

	string seqA = convertPolymerSeqToOneLetterSeq(chainA);
	string seqB = convertPolymerSeqToOneLetterSeq(chainB);

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
	 *                   === IDENTIFY INTERFACIAL POSITIONS ===
	 ******************************************************************************/
	vector<int> pos;
	vector<double> dist;
	vector<vector<vector<double>>> posDistVector;
	identifyInterface(sys, opt, PS, pos, sout, axis);

	//Setup interfacial positions vectors
	vector<int> variableInterfacialPositions = interface01(sys, pos, false);//only positions that have alternate amino acids
	vector<int> allInterfacialPositions = interface01(sys, pos);//all positions including the termini where leucines are kept fixed (this determine which positions have higher rotamers)

	//String for the positions of the sequences that are considered interface for positions amd high rotamers
	string interfaceDiffAA = getInterfaceString(variableInterfacialPositions, opt.backboneLength);
	string interfacePos = getInterfaceString(allInterfacialPositions, opt.backboneLength);

	//String for the alternateIds at the interface
	string alternateIds = getAlternateIdString(opt.Ids);

	/******************************************************************************
	 *                      === TRANSFORM TO CHOSEN GEOMETRY ===
	 ******************************************************************************/
	// Objects used for transformations
	Transforms trans; 
	trans.setTransformAllCoors(true); // transform all coordinates (non-active rotamers)
	trans.setNaturalMovements(true); // all atoms are rotated such as the total movement of the atoms is minimized

	// Transformation to zShift, axialRotation, crossingAngle, and xShift
	transformation(apvChainA, apvChainB, axisA, axisB, ori, xAxis, zAxis, opt.zShift, opt.axialRotation, opt.crossingAngle, opt.xShift, trans);
	moveZCenterOfCAMassToOrigin(sys.getAtomPointers(), helicalAxis.getAtomPointers(), trans);
	
	sys.buildAllAtoms();

	/******************************************************************************
	 *     === INITIALIZE POLYLEU WITH ALTERNATE IDENTITIES AT INTERFACE ===
	 ******************************************************************************/
	string polyLeu = generatePolyLeu("L", opt.backboneLength);
	string polyLeuPS = generateMultiIDPolymerSequence(polyLeu, opt.thread, opt.Ids, variableInterfacialPositions);
	PolymerSequence PL(polyLeuPS);

	/******************************************************************************
	 *                   === BEGINNING OUTPUT FOR OUT FILE ===
	 ******************************************************************************/
	if (opt.verbose){
		sout << "Sequence: " << polyLeu << endl;
		sout << "DiffPos:  " << interfaceDiffAA << endl;
		sout << "DiffRots: " << interfacePos << endl;
		sout << "Alternate Ids: " << alternateIds << endl;
		sout << "RotLevel: " << opt.SL << endl;
		sout << "RotLevelInterface: " << opt.SLInterface << endl << endl;
		cout << "Sequence: " << polyLeu << endl;
		cout << "DiffPos:  " << interfaceDiffAA << endl;
		cout << "DiffRots: " << interfacePos << endl;
		cout << "Alternate Ids: " << alternateIds << endl;
		cout << "RotLevel: " << opt.SL << endl;
		cout << "RotLevelInterface: " << opt.SLInterface << endl << endl;
	}

	/******************************************************************************
	 *                   === DECLARE SYSTEM FOR POLYLEU ===
	 ******************************************************************************/
	System sysL;
	CharmmSystemBuilder CSBL(sysL,opt.topFile,opt.parFile);
	CSBL.setBuildTerm("CHARMM_ELEC", false);
	CSBL.setBuildTerm("CHARMM_ANGL", false);
	CSBL.setBuildTerm("CHARMM_BOND", false);
	CSBL.setBuildTerm("CHARMM_DIHE", false);
	CSBL.setBuildTerm("CHARMM_IMPR", false);
	CSBL.setBuildTerm("CHARMM_U-BR", false);

	CSBL.setBuildNonBondedInteractions(false);
	if(!CSBL.buildSystem(PL)) {
		err << "Unable to build system from " << polyLeuPS << endl;
		exit(0);
	}

	Chain & chainAL = sysL.getChain("A");
	//Chain & chainBL = sysL.getChain("B");
	
	/******************************************************************************
	 *                     === COPY BACKBONE COORDINATES ===
	 ******************************************************************************/
	sysL.assignCoordinates(sys.getAtomPointers(),false);
	sysL.buildAllAtoms();

	CSBL.updateNonBonded(10,12,50);
	
	SystemRotamerLoader sysRot(sysL, opt.rotLibFile);
	sysRot.defineRotamerSamplingLevels();
	
	// Add hydrogen bond term
	HydrogenBondBuilder hbL(sysL, opt.hBondFile);
	hbL.buildInteractions(50);//when this is here, the HB weight is correct
	
	/******************************************************************************
	 *                === CHECK TO SEE IF ALL ATOMS ARE BUILT ===
	 ******************************************************************************/
	checkIfAtomsAreBuilt(sysL, err);

	/******************************************************************************
	 *                     === INITIAL VARIABLE SET UP ===
	 ******************************************************************************/
	EnergySet* EsetL = sysL.getEnergySet();
	// Set all terms active, besides Charmm-Elec
	EsetL->setAllTermsActive();
	EsetL->setTermActive("CHARMM_ELEC", false);
	EsetL->setTermActive("CHARMM_ANGL", false);
	EsetL->setTermActive("CHARMM_BOND", false);
	EsetL->setTermActive("CHARMM_DIHE", false);
	EsetL->setTermActive("CHARMM_IMPR", false);
	EsetL->setTermActive("CHARMM_U-BR", false);
	EsetL->setTermActive("CHARMM_VDW", true);
	EsetL->setTermActive("SCWRL4_HBOND", true);
	
	// Set weights
	EsetL->setWeight("CHARMM_VDW", 1);
	EsetL->setWeight("SCWRL4_HBOND", 1);

	/******************************************************************************
	 *                === DELETE TERMINAL HYDROGEN BOND INTERACTIONS ===
	 ******************************************************************************/
	deleteTerminalHydrogenBondInteractions(sysL,opt);

	/******************************************************************************
	 *                     === ADD IN BASELINE ENERGIES ===
	 ******************************************************************************/
	BaselineEnergyBuilder beb; //(sysL, "/exports/home/gloiseau/mslib/trunk_AS/myProgs/gloiseau/par_baseline.txt");
	beb.setSystem(sysL);//had to have this before readParameters to get it to work! So it works now

	//TODO: add in options here to use these or not (theoretically there could be an option to calculate these...or at least direct someone to calculate these?
	//initialize baseline maps to calculate energy for each sequence for comparison in baselineMonomerComparison_x.out
	map<string, double> selfMap = readSingleParameters(opt.selfEnergyFile);
	map<string, double> seqEntMap = readSingleParameters(opt.seqEntropyFile);
	map<string,map<string,map<uint,double>>> pairMap = readPairParameters(opt.pairEnergyFile);
	buildSelfInteractions(sysL, selfMap);
	buildPairInteractions(sysL, pairMap);

	//initialize baselineAAComposition energy map (based on Rosetta baselineAAComposition to prevent unlikely sequences by adding energy (ex. if more than 2PHE in sequence, add 100 energy score for each additional PHE)
	BaselineAAComposition bac(&sysL);
	bac.readPenaltyFile(opt.AACompositionPenaltyFile);
	EsetL->addInteraction(new BaselineAAComposition(bac));

	/******************************************************************************
	 *                      === TRANSFORM TO COORDINATES ===
	 ******************************************************************************/
	// Objects used for transformations
	Transforms transL; 
	transL.setTransformAllCoors(true); // transform all coordinates (non-active rotamers)
	transL.setNaturalMovements(true); // all atoms are rotated such as the total movement of the atoms is minimized
	
	vector<vector<string>> linkedPos = positionToString(sysL, variableInterfacialPositions);
	sysL.setLinkedPositions(linkedPos);
	
	loadRotamers(sysL, sysRot, opt.SL);
	loadInterfacialRotamers(sysL, sysRot, opt.SLInterface, allInterfacialPositions);

	/******************************************************************************
	 *                        === SETUP SPM AND RUN DEE ===
	 ******************************************************************************/
	//Random Number Generator
	RandomNumberGenerator RNG;
	RNG.setTimeBasedSeed();
	
	CSBL.updateNonBonded();
	sysL.buildAllAtoms();

	SelfPairManager spm;
	spm.seed(RNG.getSeed());
	spm.setSystem(&sysL);
	spm.setVerbose(false);
	spm.setRunDEE(opt.runDEESingles, opt.runDEEPairs);
	spm.setOnTheFly(true);
	spm.saveEnergiesByTerm(true);
	spm.setMCOptions(opt.MCStartTemp, opt.MCEndTemp, 50000, opt.MCCurve, 2000, 100, 0.01);
	
	//Setup running SCMF or UnbiasedMC
	if (opt.runSCMF == true){
		sout << "Running Self Consistent Mean Field" << endl;
		spm.setRunSCMF(true);
		spm.setRunSCMFBiasedMC(true);
		spm.setRunUnbiasedMC(false);
	}
	else{
		sout << "runSCMF is false; Run Unbiased Monte Carlo " << endl;
		spm.setRunSCMF(false);
		spm.setRunSCMFBiasedMC(false);
		spm.setRunUnbiasedMC(true);
	}

	if (opt.verbose){
		sout << "***SEQUENCE OPTIMIZATION***" << endl;
		cout << "***SEQUENCE OPTIMIZATION***" << endl;
		sout << "Starting SelfPairManager Optimization..." << endl << endl;
		sout << "SPM Seed: " << RNG.getSeed() << endl;
		sout << "Total interactions calced: " << EsetL->getTotalNumberOfInteractionsCalculated() << endl;
		cout << "Total interactions calced: " << EsetL->getTotalNumberOfInteractionsCalculated() << endl;
	}

	sysL.calcEnergy();
	cout << sysL.getEnergySummary() << endl;
	time(&spmStart);
	spm.runOptimizer();
	time(&spmEnd);
	
	spmTime = difftime (spmEnd, spmStart);
	
	vector<unsigned int> bestState = spm.getBestSCMFBiasedMCState();
	//double bestStatevdw = spm.getStateEnergy(bestState,"CHARMM_VDW");
	double bestStateEnergy = spm.getStateEnergy(bestState);

	if (opt.verbose){
		sout << endl << "End SelfPairManager Optimization" << endl;
		cout << endl << "End SelfPairManager Optimization" << endl;
		//TODO: would be nice to output the run times for DEE and SCMF
		sout << "SelfPairManager runOptimizer time: " << spmTime << " seconds" << endl;
		sout << "States after SCMF: " << spm.getBestSCMFBiasedMCStates().size() << endl << endl;
	}

	//Check if the van der Waals in the best state is less than 0; else, break and end run
	if (bestStateEnergy > 1000){
		cerr << "SCMF best state contains a clash; energy too high: " << bestStateEnergy << endl;
		cerr << "Geometry not favorable for design: xShift: " << opt.xShift << "; crossingAngle: " << opt.crossingAngle << "; axialRotation: " << opt.axialRotation << "; zShift: " << opt.zShift << endl;
		sout << "SCMF best state contains a clash; energy too high: " << bestStateEnergy << endl;
		sout << "Geometry not favorable for design: xShift: " << opt.xShift << "; crossingAngle: " << opt.crossingAngle << "; axialRotation: " << opt.axialRotation << "; zShift: " << opt.zShift << endl;
		err << "SCMF best state contains a clash; energy too high: " << bestStateEnergy << endl;
		err << "Geometry not favorable for design: xShift: " << opt.xShift << "; crossingAngle: " << opt.crossingAngle << "; axialRotation: " << opt.axialRotation << "; zShift: " << opt.zShift << endl;
		exit(0);
	}

	/******************************************************************************
	 *           === METHODS FOR DETERMINING ALTERNATE SEQUENCES ===
	 ******************************************************************************/
	vector<string> seqs;
	vector<string> allSeqs;

	//Initialize energyMap to hold all energies for output into a summary file
	map<string, map<string,double>> seqEnergyMap;
	map<string, map<string,double>> allSeqEnergyMap;
	map<vector<uint>, map<string,double>> stateEnergyMap;
	map<vector<uint>, map<string,double>> allStateEnergyMap;

	vector<vector<vector<unsigned int>>> monomerMinState;
	vector<int> monomerInterfacialPositions;
	
	vector<pair<string,vector<uint>>> seqStatePair;
	
	string polyLeuMonoPS = generateMonomerMultiIDPolymerSequence(polyLeu, opt.thread, opt.Ids, variableInterfacialPositions);
	string baselineCompareMonoPS = generateMonomerMultiIDPolymerSequence(polyLeu, 1, opt.Ids, variableInterfacialPositions);
	PolymerSequence monoPS(polyLeuMonoPS);
	PolymerSequence baselinePS(baselineCompareMonoPS);
	if (opt.runMCAfterSPM){
		/******************************************************************************
		 *      === MONTE CARLO TO RANDOMIZE SEQUENCES FROM BEST SCMF STATE ===
		 ******************************************************************************/
		vector<int> variableInterfacialPositionsList = getVariablePos(variableInterfacialPositions);
		
		SelfPairManager seSpm;
		seSpm.seed(RNG.getSeed());
		seSpm.setSystem(&sysL);
		seSpm.setVerbose(opt.verbose);
		seSpm.getMinStates()[0];
		seSpm.updateWeights();
		seSpm.setOnTheFly(true);
		seSpm.saveEnergiesByTerm(true);
		seSpm.calculateEnergies();

		cout << "Start State MC! " << endl;

		stateMC(sysL, opt, trans, seqEnergyMap, stateEnergyMap, seSpm, bestState, seqs, allSeqs, seqStatePair, variableInterfacialPositionsList, allInterfacialPositions, RNG, selfMap, seqEntMap, pairMap, sout, err);
	} else {
		/******************************************************************************
		 *              === RETRIEVE ALL UNIQUE SEQUENCES FROM DEE SCMF  ===
		 ******************************************************************************/
		if (spm.getBestSCMFBiasedMCStates().size() > 0){
			//TODO: make sure this actually works; I need to add ways to get in the energy terms that are found in sequenceMC
			cout << "Number of good SCMF states: " << spm.getBestSCMFBiasedMCStates().size() << endl;
			for (int i=0; i<spm.getBestSCMFBiasedMCStates().size(); i++){
				if (i < 100){
					vector <unsigned int> stateVec = spm.getBestSCMFBiasedMCStates()[i];
					sysL.setActiveRotamers(stateVec);//add in sequence checker here
					sysL.buildAtoms();
					string seq = convertPolymerSeqToOneLetterSeq(chainAL);
					bool sameSeq = sameSequenceChecker(seq, seqs);
					//cout << "Sequence " << i << ": " << seq << endl;
					sysL.calcEnergy();
				}
				else{
					i = spm.getBestSCMFBiasedMCStates().size();
				}
			}
		}
		else{
			cout << "SCMF didn't run" << endl;
		}
	}

	//If want an energyLandscape output, need to use allSeqs
	if (opt.energyLandscape){
		seqs = allSeqs;
	}

	/******************************************************************************
	 *            === CALCULATE MONOMER ENERGIES OF EACH SEQUENCE ===
	 ******************************************************************************/
	vector<double> monomerEnergiesNoIMM1;
	vector<double> monomerEnergies;
	
	time_t startTimeMono, endTimeMono;
	double diffTimeMono;
	time(&startTimeMono);

	calculateMonomerEnergiesNoMoves(baselinePS, opt, RNG, seqs, seqEnergyMap, monomerEnergiesNoIMM1, sout);
	calculateMonomerEnergies(sysL, monoPS, opt, trans, RNG, seqs, seqEnergyMap, monomerEnergies, monomerInterfacialPositions, sout);

	time(&endTimeMono);
	diffTimeMono = difftime (endTimeMono, startTimeMono);
	cout << "Monomer Time: "  << diffTimeMono << "s" << endl;

	/******************************************************************************
	 *               === LOCAL REPACKS ON EACH UNIQUE SEQUENCE ===
	 ******************************************************************************/
	vector<double> xShifts;
	vector<double> crossingAngles;
	vector<double> axialRotations;
	vector<double> zShifts;
	vector<double> dimerEnergies;
	vector<double> finalEnergies;

	// Setup timer for LocalMC Cycles
	time_t startTimeLMC, endTimeLMC;
	double diffTimeLMC;
	time(&startTimeLMC);
	
	// Initialize PDBWriter for design
	PDBWriter writer;
	writer.open(opt.pdbOutputDir + "/design_" + opt.runNumber + ".pdb");

	//TODO: change this to go through the energies of dimers from the sequenceMC and do them in order
	//TODO: should I change this to only do localRepacks on sequences of really bad energy (like lowest tier or something?) or maybe if the energy calculated wasn't better than monomer energy?
	if (opt.runLocalMC){
		sout << "***LOCAL REPACKS ON UNIQUE SEQUENCES***" << endl << endl;
		localMC(sysL, helicalAxis, opt, PL, RNG, seqs, allInterfacialPositions, linkedPos, seqEnergyMap, monomerEnergies, dimerEnergies, finalEnergies, xShifts, crossingAngles, axialRotations, zShifts, sout, err, writer);
		
		time(&endTimeLMC);
		diffTimeLMC = difftime (endTimeLMC, startTimeLMC);
		cout << "End Local Monte Carlo Repacks: " << diffTimeLMC << "s" << endl;
		sout << "End Local Monte Carlo Repacks: " << diffTimeLMC << "s" << endl;
	}
	else{//TODO: think of things I can use pointers for (maybe the energy map?); it could be lagging because of the sheer amount of data it has to hold (lags at the end of this step)
		sout << "***CALCULATE DIMER ENERGIES WITHOUT LOCAL REPACKS***" << endl << endl;
		calculateDimerEnergies(sysL, PL, opt, seqs, seqStatePair, seqEnergyMap, monomerEnergies, dimerEnergies, finalEnergies, allInterfacialPositions, linkedPos, sout, writer);
		
		time(&endTimeLMC);
		diffTimeLMC = difftime (endTimeLMC, startTimeLMC);
		cout << "End Dimer Calculations Without Local Repacks: " << diffTimeLMC << "s" << endl;
		sout << "End Dimer Calculations Without Local Repacks: " << diffTimeLMC << "s" << endl;
	}

	cout << "#Sequence:    " << seqs.size() << endl;
	cout << "#DimerEner:   " << dimerEnergies.size() << endl;
	cout << "#MonomerEner: " << monomerEnergies.size() << endl;
	cout << "#FinalEner:   " << finalEnergies.size() << endl;
	for (uint i=0; i<seqs.size(); i++){
		cout << seqs[i] << ": " << dimerEnergies[i] << "-" << monomerEnergies[i] << "=" << finalEnergies[i] << endl; 
	}

	/******************************************************************************
	 *                   === WRITE OUT FINAL DESIGN FILE ===
	 ******************************************************************************/
	// Initialize finalDesignInfo file 
	ofstream fout;
	string foutfile = opt.pdbOutputDir + "/finalDesignInfo.out";
	fout.open(foutfile.c_str());
	fout << "\t";	
	cout << "\t";
	string tab = "\t";
	for (uint i=0; i<opt.energyTermsToOutput.size(); i++){
		fout << opt.energyTermsToOutput[i] << tab;
		cout << opt.energyTermsToOutput[i] << tab;
	}
	if (opt.runLocalMC){
		fout << "startXShift" << tab << "startCrossAng" << tab << "startAxialRot" << tab << "startZShift" << tab << "xShift" << tab << "crossAng" << tab << "axialRot" << tab << "zShift" << tab << "Sequence" << tab << "PDBPath" << tab << "Thread" << tab << "Interface" << endl;
		cout << "startXShift" << tab << "startCrossAng" << tab << "startAxialRot" << tab << "startZShift" << tab << "xShift" << tab << "crossAng" << tab << "axialRot" << tab << "zShift" << tab << "Sequence" << tab << "PDBPath" << tab << "Thread" << tab << "Interface" << endl;
	}
	else{
		fout << "startXShift" << tab << "startCrossAng" << tab << "startAxialRot" << tab << "startZShift" << tab << "Sequence" << tab << "PDBPath" << tab << "Thread" << tab << "Interface" << endl;
		cout << "startXShift" << tab << "startCrossAng" << tab << "startAxialRot" << tab << "startZShift" << tab << "Sequence" << tab << "PDBPath" << tab << "Thread" << tab << "Interface" << endl;
	}

	//Output the final energies into the finalDesignInfo.out file: Order of output is currently set in the config file
	for (uint i=0; i<seqs.size(); i++){
		string sequence = seqs[i];
		cout << "Sequence Info:" << tab;
		fout << "Sequence Info:" << tab;
		map<string,double> energyMap = seqEnergyMap.at(sequence);
		for (uint j=0; j<opt.energyTermsToOutput.size(); j++){
			cout << energyMap.at(opt.energyTermsToOutput[j]) << tab;
			fout << energyMap.at(opt.energyTermsToOutput[j]) << tab;
		}
		if (opt.runLocalMC){
			cout << opt.xShift << tab << opt.crossingAngle << tab << opt.axialRotation << tab << opt.zShift << tab << xShifts[i] << tab << crossingAngles[i] << tab << axialRotations[i] << tab << zShifts[i] << tab << sequence << tab << opt.pdbOutputDir << "/design_" << i << ".pdb" << tab << opt.thread << tab << interfacePos << endl << endl;
			fout << opt.xShift << tab << opt.crossingAngle << tab << opt.axialRotation << tab << opt.zShift << tab << xShifts[i] << tab << crossingAngles[i] << tab << axialRotations[i] << tab << zShifts[i] << tab << sequence << tab << opt.pdbOutputDir << "/design_" << i << ".pdb" << tab << opt.thread << tab << interfacePos << endl << endl;
		}
		else{
			cout << opt.xShift << tab << opt.crossingAngle << tab << opt.axialRotation << tab << opt.zShift << tab << sequence << tab << opt.pdbOutputDir << "/design_" << i << ".pdb" << tab << opt.thread << tab << interfacePos << endl << endl;
			fout << opt.xShift << tab << opt.crossingAngle << tab << opt.axialRotation << tab << opt.zShift << tab << sequence << tab << opt.pdbOutputDir << "/design_" << i << ".pdb" << tab << opt.thread << tab << interfacePos << endl << endl;
		}
	}

	time(&endTime);
	diffTime = difftime (endTime, startTime);
	sout << "Total Time: " << setiosflags(ios::fixed) << setprecision(0) << diffTime << " seconds" << endl;
	fout  << "Total Time: " << setiosflags(ios::fixed) << setprecision(0) << diffTime << " seconds" << endl;
	cout  << "Total Time: " << setiosflags(ios::fixed) << setprecision(0) << diffTime << " seconds" << endl;

	writer.close();
	fout.close();
	err.close();
	sout.close();
}

/*********************************
 *  
 *  ======= FUNCTIONS =======
 *
 *********************************/



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
	 *  /exports/home/gloiseau/mslib/trunk_AS/myProgs/gloiseau/helixGenerator.config
	 *  
	 ******************************************/

	vector<string> required;
	vector<string> allowed;

	//opt.required.push_back("");
	//opt.allowed.push_back("");

	//opt.allowed.push_back("");
	// optional
	opt.allowed.push_back("useGeoFromPDBData");
	
	opt.allowed.push_back("sequence");
	opt.allowed.push_back("backboneAA");
	opt.allowed.push_back("backboneLength");
	
	opt.allowed.push_back("startResNum");
	opt.allowed.push_back("sequenceStart");
	opt.allowed.push_back("endResNum");
	opt.allowed.push_back("tmStart");
	opt.allowed.push_back("tmEnd");

	opt.allowed.push_back("xShift");
	opt.allowed.push_back("zShift");
	opt.allowed.push_back("axialRotation");
	opt.allowed.push_back("crossingAngle");
	opt.allowed.push_back("transform");

	//localMC repack variables
	opt.allowed.push_back("MCCycles");
	opt.allowed.push_back("MCMaxRejects");
	opt.allowed.push_back("MCStartTemp");
	opt.allowed.push_back("MCEndTemp");
	opt.allowed.push_back("MCCurve");
	
	opt.allowed.push_back("deltaZ");
	opt.allowed.push_back("deltaAx");
	opt.allowed.push_back("deltaCross");
	opt.allowed.push_back("deltaX");

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
	opt.allowed.push_back("numberOfStructuresToMCRepack");
	opt.allowed.push_back("energyCutOff");
	
	opt.allowed.push_back("inputMonomerE");
	opt.allowed.push_back("monoE_vdw");
	opt.allowed.push_back("monoE_hbond");
	opt.allowed.push_back("monoE_solv");
	opt.allowed.push_back("monoE_solvRef");

	opt.allowed.push_back("printAllCrds");
	opt.allowed.push_back("printAxes");
	opt.allowed.push_back("printTermEnergies");
	opt.allowed.push_back("deleteTerminalHbonds");

	//Input Files
	opt.allowed.push_back("topFile");
	opt.allowed.push_back("parFile");
	opt.allowed.push_back("baselineFile");
	opt.allowed.push_back("geometryDensityFile");
	opt.allowed.push_back("solvFile");
	opt.allowed.push_back("rotLibFile");
	opt.allowed.push_back("backboneCrd");
	opt.allowed.push_back("hbondFile");
	opt.allowed.push_back("pdbOutputDir");
	opt.allowed.push_back("infile");
	opt.allowed.push_back("kdeFile");
	opt.allowed.push_back("selfEnergyFile");
	opt.allowed.push_back("pairEnergyFile");
	opt.allowed.push_back("seqEntropyFile");
	opt.allowed.push_back("AACompositionPenaltyFile");
	opt.allowed.push_back("configfile");
	
	opt.allowed.push_back("thread");
	opt.allowed.push_back("bbThread");

	//Alternate 
	opt.allowed.push_back("Ids");

	//Command Line Arguments
	opt.allowed.push_back("runNumber");
	opt.allowed.push_back("useIMM1");

	//MonteCarlo Arguments
	opt.allowed.push_back("runMCAfterSPM");
	opt.allowed.push_back("runSequenceMC");
	opt.allowed.push_back("runLocalMC");
	opt.allowed.push_back("numberEnergyVectors");
	opt.allowed.push_back("numStatesToSave");
	opt.allowed.push_back("energyLimit");
	opt.allowed.push_back("energyDifference");

	//RNG Arguments
	opt.allowed.push_back("useTimeBasedSeed");
	opt.allowed.push_back("energyLandscape");
	
	//SelfPairManager Arguments
	opt.allowed.push_back("runDEESingles");
	opt.allowed.push_back("runDEEPairs");
	opt.allowed.push_back("runSCMF");
	opt.allowed.push_back("pairDist");
	
	//Energy Terms to Output
	opt.allowed.push_back("monomerEnergyTerms");
	opt.allowed.push_back("monomerIMM1EnergyTerms");
	opt.allowed.push_back("dimerEnergyTerms");
	opt.allowed.push_back("calcEnergyOfSequenceTerms");
	opt.allowed.push_back("sequenceMCEnergyTerms");
	opt.allowed.push_back("enerLandscapeTerms");
	opt.allowed.push_back("energyTermsToOutput");

	opt.allowed.push_back("energyTermList");
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
	
	opt.useGeoFromPDBData = OP.getBool("useGeoFromPDBData");
	if (OP.fail()) {
		opt.warningMessages += "useGeoFromPDBData not specified, defaulting to false\n";
		opt.warningFlag = true;
		opt.useGeoFromPDBData = false;
	}
	
	opt.runNumber = OP.getString("runNumber");
	if (OP.fail()) {
		opt.warningMessages += "runNumber not specified, using 1\n";
		opt.warningFlag = true;
		opt.runNumber = MslTools::intToString(1);
	}

	opt.pairDist = OP.getInt("pairDist");
	if (OP.fail()){
		opt.warningMessages += "pairDist not specified, using 15\n";
		opt.warningFlag = true;
		opt.pairDist = 15;
	}

	opt.useIMM1 = OP.getBool("useIMM1");
	if (OP.fail()) {
		opt.warningMessages += "useIMM1 not specified, defaulting to false\n";
		opt.warningFlag = true;
		opt.useIMM1 = false;
	}
	
	opt.printAllCrds = OP.getBool("printAllCrds");
	if (OP.fail()) {
		opt.warningMessages += "printAllCrds not specified using false\n";
		opt.warningFlag = true;
		opt.printAllCrds = false;
	}
	opt.printAxes = OP.getBool("printAxes");
	if (OP.fail()) {
		opt.warningMessages += "printAxes not specified using false\n";
		opt.warningFlag = true;
		opt.printAxes = false;
	}
	opt.printTermEnergies = OP.getBool("printTermEnergies");
	if (OP.fail()) {
		opt.printTermEnergies = true;
		opt.warningMessages += "printTermEnergies not specified using true\n";
		opt.warningFlag = true;
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
		opt.tmEnd = opt.sequenceLength;
		opt.warningMessages += "tmEnd not specified using " + MslTools::intToString(opt.tmEnd) + "\n";
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
		opt.warningMessages += "xShift not specified, defaulting to ...\n";
		opt.warningFlag = true;
		opt.xShift = 6.7;
	}
	opt.zShift = OP.getDouble("zShift");
	if (OP.fail()) {
		opt.warningMessages += "zShift not specified, defaulting to ...\n";
		opt.warningFlag = true;
		opt.zShift = 0;
	}
	opt.axialRotation = OP.getDouble("axialRotation");
	if (OP.fail()) {
		opt.warningMessages += "axialRotation not specified, defaulting to ...\n";
		opt.warningFlag = true;
		opt.axialRotation = 0;
	}
	opt.crossingAngle = OP.getDouble("crossingAngle");
	if (OP.fail()) {
		opt.warningMessages += "crossingAngle not specified, defaulting to ...\n";
		opt.warningFlag = true;
		opt.crossingAngle = -40;
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
	if (opt.thread == 0) {
		if (opt.sequenceLength > opt.backboneLength){
			opt.bbThread = opt.sequenceLength - opt.backboneLength + 1;
		}
		else{
			opt.bbThread = opt.backboneLength - opt.sequenceLength + 1;
		}
	}
	//opt.thread = opt.bbThread;
		
	//localMC repack variables
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

	opt.deltaZ = OP.getDouble("deltaZ");
	if (OP.fail()) {
		opt.warningMessages += "deltaZ not specified using 0.1\n";
		opt.warningFlag = true;
		opt.deltaZ = 0.1;
	}
	opt.deltaAx = OP.getDouble("deltaAx");
	if (OP.fail()) {
		opt.warningMessages += "deltaAx not specified using 1.0\n";
		opt.warningFlag = true;
		opt.deltaAx = 1.0;
	}
	opt.deltaCross = OP.getDouble("deltaCross");
	if (OP.fail()) {
		opt.warningMessages += "deltaCross not specified using 1.0\n";
		opt.warningFlag = true;
		opt.deltaCross = 1.0;
	}
	opt.deltaX = OP.getDouble("deltaX");
	if (OP.fail()) {
		opt.warningMessages += "deltaX not specified using 0.1\n";
		opt.warningFlag = true;
		opt.deltaX = 0.1;
	}

	opt.verbose = OP.getBool("verbose");
	if (OP.fail()) {
		opt.warningMessages += "verbose not specified using false\n";
		opt.warningFlag = true;
		opt.verbose = false;
	}
	opt.greedyCycles = OP.getInt("greedyCycles");
	if (OP.fail()) {
		opt.warningMessages += "greedyCycles not specified using 10\n";
		opt.warningFlag = true;
		opt.greedyCycles = 10;
	}
	opt.numberOfStructuresToMCRepack = OP.getInt("numberOfStructuresToMCRepack");
	if (OP.fail()) {
		opt.warningMessages += "numberOfStructuresToMCRepack not specified using 20\n";
		opt.warningFlag = true;
		opt.numberOfStructuresToMCRepack = 20;
	}
	opt.energyCutOff = OP.getDouble("energyCutOff");
	if (OP.fail()) {
		opt.warningMessages += "energyCutOff not specified using 100.0\n";
		opt.warningFlag = true;
		opt.energyCutOff = 100.0;
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
	opt.weight_seqEntropy = opt.weight_seqEntropy*100;//Default allows 1 to be weighted equally to other energy terms (I should convert to actual weighting conversion used with other energy terms)

	//rotlevel
	opt.SL = OP.getString("SL");
	if (OP.fail()) {
		opt.warningFlag = true;
		opt.warningMessages += "SL not specified, default to SL70\n";
		opt.SL = "SL70.00";
	}
	else{
		opt.SL = "SL"+opt.SL;
	}
	opt.SLInterface = OP.getString("SLInterface");
	if (OP.fail()) {
		opt.warningFlag = true;
		opt.warningMessages += "SL not specified, default to SL70\n";
		opt.SL = "SL70.00";
	}
	else{
		opt.SLInterface = "SL"+opt.SLInterface;
	}

	opt.backboneLength = OP.getInt("backboneLength");
	if (OP.fail()) {
		opt.warningFlag = true;
		opt.warningMessages += "backboneLength not specified, default to 35\n";
		opt.backboneLength = 35;
	}

	opt.inputMonomerE = OP.getBool("inputMonomerE");
	if (OP.fail()) {
		opt.warningMessages += "monomer energy will be calculated\n";
		opt.warningFlag = true;
		opt.inputMonomerE = true;
	}
	opt.monoE_vdw = OP.getDouble("monoE_vdw");
	if (OP.fail()) {
		opt.monoE_vdw = 1000000; //Default large, easy to spot error.
	}
	opt.monoE_hbond = OP.getDouble("monoE_hbond");
	if (OP.fail()) {
		opt.monoE_hbond = 1000000; //Default large, easy to spot error.
	}
	opt.monoE_solv = OP.getDouble("monoE_solv");
	if (OP.fail()) {
		opt.monoE_solv = 1000000; //Default large, easy to spot error.
	}
	opt.monoE_solvRef = OP.getDouble("monoE_solvRef");
	if (OP.fail()) {
		opt.monoE_solvRef= 1000000; //Default large, easy to spot error.
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

	opt.baselineFile = OP.getString("baselineFile");
	if (OP.fail()) {
		opt.errorMessages += "Unable to determine baselineFile, no baseline forces used\n";
		//opt.errorFlag = true;
	}
	opt.geometryDensityFile = OP.getString("geometryDensityFile");
	if (OP.fail()) {
		opt.warningMessages += "Unable to determine geometryDensityFile, defaulting to original density file\n";
		opt.warningFlag = true;
		opt.geometryDensityFile = "/exports/home/gloiseau/mslib/trunk_AS/myProgs/gloiseau/2021_05_27_90cutoff_kde.txt";
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
	opt.monoRotLibFile = OP.getString("monoRotLibFile");
	if (OP.fail()) {
		opt.warningMessages += "monoRotLibFile not specified using " + opt.rotLibFile + "\n";
		opt.warningFlag = true;
		opt.monoRotLibFile = opt.rotLibFile;
	}

	opt.backboneCrd = OP.getString("backboneCrd");
	if (OP.fail()) {
		opt.errorMessages += "Unable to determine backboneCrd";
		opt.errorFlag = true;
	}
	
	opt.hBondFile = OP.getString("hbondFile");
	if (OP.fail()) {
		string envVar = "MSL_HBOND_CA_PAR";
		if(SYSENV.isDefined(envVar)) {
			opt.hBondFile = SYSENV.getEnv(envVar);
			opt.warningMessages += "hbondFile not specified using " + opt.hBondFile + "\n";
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
	
	opt.kdeFile = OP.getString("kdeFile");
	if (OP.fail()) { 
		opt.warningMessages += "kdeEnergyFile not specified, default \n";
		opt.warningFlag = true;
		opt.kdeFile = "/exports/home/gloiseau/mslib/trunk_AS/myProgs/gloiseau/kde.txt";
	}
	opt.selfEnergyFile = OP.getString("selfEnergyFile");
	if (OP.fail()) { 
		opt.warningMessages += "selfEnergyFile not specified, default \n";
		opt.warningFlag = true;
		opt.selfEnergyFile = "/exports/home/gloiseau/mslib/trunk_AS/myProgs/gloiseau/2020_10_07_meanSelf_par.txt";
	}
	opt.pairEnergyFile = OP.getString("pairEnergyFile");
	if (OP.fail()) { 
		opt.warningMessages += "pairEnergyFile not specified, default \n";
		opt.warningFlag = true;
		opt.pairEnergyFile = "/exports/home/gloiseau/mslib/trunk_AS/myProgs/gloiseau/2020_10_07_meanPair_par.txt";
	}
	opt.seqEntropyFile = OP.getString("seqEntropyFile");
	if (OP.fail()) { 
		opt.warningMessages += "seqEntropyFile not specified, default to /data01/sabs/tmRepacks/pdbFiles/69-gly-residue-helix.pdbi\n";
		opt.warningFlag = true;
		opt.seqEntropyFile = "/exports/home/gloiseau/mslib/trunk_AS/myProgs/gloiseau/seqEntropies.txt";
	}
	opt.AACompositionPenaltyFile = OP.getString("AACompositionPenaltyFile");
	if (OP.fail()) { 
		opt.warningMessages += "AACompositionPenaltyFile not specified, default \n";
		opt.warningFlag = true;
		opt.AACompositionPenaltyFile = "/exports/home/gloiseau/mslib/trunk_AS/myProgs/gloiseau/AACompositionPenalties.out";
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
	opt.runMCAfterSPM = OP.getBool("runMCAfterSPM");
	if (OP.fail()){
		opt.errorMessages += "runMCAfterSPM not specified, defaulting to true";
		opt.warningFlag = true;
		opt.runMCAfterSPM = true;
	}
	opt.runLocalMC = OP.getBool("runLocalMC");
	if (OP.fail()){
		opt.errorMessages += "runLocalMC not specified, defaulting to true";
		opt.warningFlag = true;
		opt.runLocalMC = true;
	}
	opt.runSequenceMC = OP.getBool("runSequenceMC");
	if (OP.fail()){
		opt.errorMessages += "runSequenceMC not specified, defaulting to true";
		opt.warningFlag = true;
		opt.runSequenceMC = true;
	}
	opt.numberEnergyVectors = OP.getInt("numberEnergyVectors");
	if (OP.fail()){
		opt.errorMessages += "numberEnergyVectors not specified, defaulting to 5";
		opt.warningFlag = true;
		opt.numberEnergyVectors = 5;
	}
	opt.numStatesToSave = OP.getInt("numStatesToSave");
	if (OP.fail()){
		opt.errorMessages += "numStatesToSave not specified, defaulting to 5";
		opt.warningFlag = true;
		opt.numStatesToSave = 5;
	}
	opt.energyLimit = OP.getInt("energyLimit");
	if (OP.fail()){
		opt.errorMessages += "energyLimit not specified, defaulting to -35";
		opt.warningFlag = true;
		opt.energyLimit = -35;
	}
	opt.energyDifference = OP.getInt("energyDifference");
	if (OP.fail()){
		opt.errorMessages += "energyDifference not specified, defaulting to 5";
		opt.warningFlag = true;
		opt.energyDifference = 5;
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

	//Energy Terms to Output
	opt.monomerEnergyTerms = OP.getStringVector("monomerEnergyTerms");
	if (OP.fail()) {
		opt.warningMessages += "Unable to identify monomer energy terms, defaulting to Monomer, VDWMonomer, HbondMonomer, IMM1Monomer, MonomerSelfBaseline, MonomerPairBaseline\n";
		opt.warningFlag = true;
	}
	opt.monomerIMM1EnergyTerms = OP.getStringVector("monomerIMM1EnergyTerms");
	if (OP.fail()) {
		opt.warningMessages += "Unable to identify monomerIMM1 energy terms, defaulting to Monomerw/IMM1, VDWMonomerw/IMM1, HbondMonomerw/IMM1, Monomerw/IMM1SelfBaseline, Monomerw/IMM1PairBaseline\n";
		opt.warningFlag = true;
	}
	opt.dimerEnergyTerms = OP.getStringVector("dimerEnergyTerms");
	if (OP.fail()) {
		opt.warningMessages += "Unable to identify dimer energy terms, defaulting to Dimer, VDWDimer, HbondDimer, IMM1Dimer, DimerSelfBaseline, DimerPairBaseline\n";
		opt.warningFlag = true;
	}
	opt.calcEnergyOfSequenceTerms = OP.getStringVector("calcEnergyOfSequenceTerms");
	if (OP.fail()) {
		opt.warningMessages += "Unable to identify dimer energy terms, defaulting to Dimer, VDWDimer, HbondDimer, IMM1Dimer, DimerSelfBaseline, DimerPairBaseline\n";
		opt.warningFlag = true;
	}
	opt.sequenceMCEnergyTerms = OP.getStringVector("sequenceMCEnergyTerms");
	if (OP.fail()) {
		opt.warningMessages += "Unable to identify sequence energy terms, defaulting to Monomer, VDWMonomer, HbondMonomer, IMM1Monomer, MonomerSelfBaseline, MonomerPairBaseline, DimerSelfBaseline, DimerPairBaseline, EnergyBeforeLocalMC\n";
		opt.warningFlag = true;
	}
	opt.enerLandscapeTerms = OP.getStringVector("enerLandscapeTerms");
	if (OP.fail()) {
		opt.warningMessages += "Unable to identify sequence energy terms, defaulting to PrevEnergyTotal, CurrEnergyTotal, PrevSeqProp, CurrSeqProp, PrevSeqEntropy, CurrSeqEntropy\n";
		opt.warningFlag = true;
	}
	opt.energyTermsToOutput = OP.getStringVector("energyTermsToOutput");
	if (OP.fail()) {
		opt.warningMessages += "Unable to identify sequence energy terms, defaulting to Monomer, VDWMonomer, HbondMonomer, IMM1Monomer, MonomerSelfBaseline, MonomerPairBaseline, DimerSelfBaseline, DimerPairBaseline, EnergyBeforeLocalMC\n";
		opt.warningFlag = true;
	}
	opt.energyTermList = OP.getStringVector("energyTermList");
	if (OP.fail()) {
		opt.warningMessages += "Unable to identify sequence energy terms, defaulting to Monomer, VDWMonomer, HbondMonomer, IMM1Monomer, MonomerSelfBaseline, MonomerPairBaseline, DimerSelfBaseline, DimerPairBaseline, EnergyBeforeLocalMC\n";
		opt.warningFlag = true;
	}
	
	opt.rerunConf = OP.getConfFile();

	return opt;
}
