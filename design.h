/**
 * @Author: Gilbert Loiseau
 * @Date:   2022/02/12
 * @Email:  gjowl04@gmail.com
 * @Filename: design.h
 * @Last modified by:   Gilbert Loiseau
 * @Last modified time: 2022/02/14
 */

#ifndef DESIGN_H
#define DESIGN_H

#include <sstream>

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
#include "design_options.h"

// Design Functions: TODO figure out which of these are necessary; a lot of this code I just added internally I believe
#include "BaselineIMM1Interaction.h"
#include "BaselinePairInteraction.h"
#include "BaselineOuterPairInteraction.h"
#include "BaselineAAComposition.h"
#include "BaselineSequenceEntropy.h"
#include "BaselineSequenceEntropyNormalized.h"
#include "BaselinePermutation.h"
#include "SasaCalculator.h"

using namespace std;
using namespace MSL;

/***********************************
 *geometry
 ***********************************/
//CATM Functions
void c2Symmetry(AtomPointerVector & _apvA, AtomPointerVector & _apvB);
void moveZCenterOfCAMassToOrigin(AtomPointerVector& _apV, AtomPointerVector& _axis, Transforms & _trans);
void transformation(AtomPointerVector & _chainA, AtomPointerVector & _chainB, AtomPointerVector & _axisA, AtomPointerVector & _axisB, CartesianPoint & _ori, CartesianPoint & _xAxis, CartesianPoint & _zAxis, double _zShift, double _axialRotation, double _crossingAngle, double _xShift, Transforms & _trans);
void backboneMovement(AtomPointerVector & _chainA, AtomPointerVector & _chainB, AtomPointerVector & _axisA, AtomPointerVector & _axisB, Transforms _trans, double _deltaMove, unsigned int moveType);
void xShiftTransformation(AtomPointerVector & _chainA, AtomPointerVector & _chainB, AtomPointerVector & _axisA, AtomPointerVector & _axisB, double _xShift, Transforms & _trans);
void readGeometryFile(string _filename, vector<string>& _fileVec);
void getGeometry(Options &_opt, RandomNumberGenerator &_RNG, vector<double> &_densities, ofstream &_out);

/***********************************
 *string output
 ***********************************/
// TODO: if possible, make some of these more multipurpose and change names, and add in one or two line examples for what they do
string convertToPolymerSequenceNeutralPatch(string _seq, int _startResNum);
string convertToPolymerSequenceNeutralPatchMonomer(string _seq, int _startResNum);
string convertPolymerSeqToOneLetterSeq(Chain &_chain);
string generateString(string _backbone, int _length);
string generateBackboneSequence(string _backbone, int _length);
string generateMonomerMultiIDPolymerSequence(string _seq, int _startResNum, vector<string> _alternateIds, vector<int> _interfacialPositions);
string generatePolymerSequence(string _backboneAA, int _backboneLength, int _startResNum);
string generateMonomerPolymerSequenceFromSequence(string _sequence, int _startResNum);
string generateMultiIDPolymerSequence(string _seq, int _startResNum, vector<string> _alternateIds, vector<int> _interfacialPositions);
string getInterfaceString(vector<int> _interface, int _seqLength);
string getAlternateIdString(vector<string> _alternateIds);
string getInterfaceSequence(Options &_opt, string _interface, string _sequence);

/***********************************
 *repack functions
 ***********************************/
void repackSideChains(SelfPairManager & _spm, int _greedyCycles);
std::vector < std::vector < bool > > getActiveMask (System &_sys);

/***********************************
 *define interface and rotamer sampling
 ***********************************/
vector<int> getRotamerSampling(string _rotamerLevels);
vector<int> getLinkedPositions(vector<int> _rotamerSampling, int _interfaceLevel, int _highestRotamerLevel);
vector<uint> getVariablePositions(vector<int> &_interfacialPositions);
vector<vector<string>> convertToLinkedFormat(System &_sys, vector<int> &_interfacialPositions, int _backboneLength);
std::vector<pair <int, double> > calculateResidueBurial (System &_sys);
std::vector<pair <int, double> > calculateResidueBurial (System &_sys, Options &_opt, string _seq);
//TODO: change all of the original interfacePositions to variablePositions and the allInterfacePositions to interfacePositions
void defineInterfaceAndRotamerSampling(Options &_opt, PolymerSequence _PS, string &_rotamerLevels, string &_polySeq, string &_variablePositionString, string &_rotamerSamplingString, vector<int> &_linkedPositions, vector<uint> &_interfacePositions, vector<uint> &_variablePositions, vector<int> &_rotamerSamplingPerPosition, ofstream &_out, string _axis);

/***********************************
 *output file functions
 ***********************************/
void setupDesignDirectory(Options &_opt, string _date);
void printConfigFile(Options & _opt, ofstream & _out);
void outputEnergyFile(Options &_opt, string _interface, vector<string> _allDesigns);
void makeRepackConfig(Options &_opt, string _sequence, string _designDir, string _designNumber, string _pdbPath, string _crdPath, map<string,double> _energyMap);
void makeDockingConfig(Options &_opt, string _sequence, vector<uint> _state, string _pdbPath, map<string,double> _energyMap, vector<int> _rotamerSampling);
void outputRepackFile(Options &_opt, vector<string> _dockingDesigns);
void outputDesignFiles(Options &_opt, string _interface, vector<int> _rotamerSampling, vector<pair<string,vector<uint>>> _sequenceStatePair, map<string,map<string,double>> _sequenceEnergyMap, vector<double> _densities);

/***********************************
 *load rotamer functions
 ***********************************/
void loadMonomerRotamers(System &_sys, SystemRotamerLoader &_sysRot);
void loadRotamersBySASABurial(System &_sys, SystemRotamerLoader &_sysRot, Options &_opt, vector<int> &_rotamerSampling);
void loadInterfacialRotamers(System &_sys, SystemRotamerLoader &_sysRot, string _SL, int _numRotamerLevels, vector<int> _interface);
void loadRotamers(System &_sys, SystemRotamerLoader &_sysRot, string _SL);
void loadRotamers(System &_sys, SystemRotamerLoader &_sysRot, Options &_opt, vector<int> &_rotamerSampling);//Uses rotamer sampling defined by SASA values to load rotamers by position
void loadRotamersSPM(System &_sys, SystemRotamerLoader &_sysRot, Options &_opt);

/***********************************
 *baseline energy helper functions
 ***********************************/
vector<double> calcBaselineEnergies(System &_sys, int _seqLength);
vector<double> calcPairBaselineEnergies(System &_sys, int _seqLength);
double sumEnergyVector(vector<double> _energies);

/***********************************
 *calculate energies
 ***********************************/
void computeDimerEnergy(System &_sys, Options& _opt, map<string,map<string,double>> &_sequenceEnergyMap, string &_sequence, vector<uint> &_stateVec, vector<int> &_rotamerSampling, vector<vector<string>> &_linkedPos, int _seqNumber, RandomNumberGenerator &_RNG, PDBWriter &_writer, ofstream &_sout, ofstream &_err);
void computeDimerEnergiesLinked(System &_sys, Options &_opt, map<string,map<string,double>> &_sequenceEnergyMap, vector<pair<string,vector<uint>>> &_sequenceStatePair, vector<int> &_rotamerSampling, vector<vector<string>> &_linkedPos, RandomNumberGenerator &_RNG, PDBWriter &_writer, ofstream &_sout, ofstream &_err);
void computeDimerEnergies(System &_sys, Options &_opt, map<string, map<string,double>> &_sequenceEnergyMap, vector<pair<string,vector<uint>>> &_sequenceStatePair, vector<int> _rotamerSamplingPerPosition, vector<vector<string>> &_linkedPos, RandomNumberGenerator &_RNG, ofstream &_sout, ofstream &_err);
void computeMonomerEnergyNoIMM1(Options& _opt, map<string,map<string,double>> &_sequenceEnergyMap, string &_seq, RandomNumberGenerator &_RNG, ofstream &_sout, ofstream &_err);
void computeMonomerEnergyIMM1(Options& _opt, Transforms & _trans, map<string,map<string,double>> &_sequenceEnergyMap, string _seq, RandomNumberGenerator &_RNG, ofstream &_sout, ofstream &_err);
void computeMonomerEnergies(Options &_opt, Transforms &_trans, map<string, map<string,double>> &_sequenceEnergyMap, vector<string> &_seqs, RandomNumberGenerator &_RNG, ofstream &_sout, ofstream &_err);

/***********************************
 *other helper functions
 ***********************************/
void saveEnergyDifference(Options _opt, map<string,map<string,double>> &_sequenceEnergyMap, string _sequence);
void outputEnergiesByTerm(SelfPairManager &_spm, vector<uint> _stateVec, map<string,double> &_energyMap, vector<string> _energyTermList, string _energyDescriptor, bool _includeIMM1);
void outputEnergiesByTermLinked(EnergySet *_Eset, map<string,double> &_energyMap, vector<string> _energyTermList, string _energyDescriptor);
void deleteTerminalHydrogenBondInteractions(System &_sys, Options &_opt);
map<string, double> readSingleParameters(string _baselineFile);
map<string,map<string,map<uint, double>>> readPairParameters(string _baselineFile);

/***********************************
 *energy builders
 ***********************************/
void buildBaselineIMM1Interactions(System &_sys, map<string, double> &_selfMap);
void buildSelfInteractions(System &_sys, map<string, double> &_selfMap);
void buildPairInteractions(System &_sys, map<string,map<string,map<uint,double>>>& _pairMap);
void buildSequenceEntropy(System &_sys, map<string, double> &_sequenceEntropyMap, double _weight);

/***********************************
 *stateMC helper functions
 ***********************************/
//gets a random position and chooses a random rotamer
void randomPointMutation(System &_sys, Options &_opt, RandomNumberGenerator &_RNG, vector<uint> _variablePositions, vector<string> &_ids);
void randomPointMutationUnlinked(System &_sys, Options &_opt, RandomNumberGenerator &_RNG, vector<uint> _variablePositions, vector<string> &_ids);
void randomRotamerChange(System &_sys, Options &_opt, RandomNumberGenerator &_RNG, vector<uint> _variablePositions, vector<unsigned int> &_stateVec);
void randomRotamerChangeNonLinked(System &_sys, Options &_opt, RandomNumberGenerator &_RNG, map<int,map<int,pair<uint,uint>>> &_posRotLimitMap, vector<uint> _variablePositions, vector<unsigned int> &_stateVec);
void sameSequenceChecker(string &_newSeq, vector<string> &_seqs);
bool sameSequenceChecker(string &_newSeq, double &_newEnergy, vector<uint> &_state, vector<pair<double,string>> &_enerSeqPair, vector<pair<double,vector<uint>>> &_energyStateVec);
double getMapValueFromKey(map<string,double> &_map, string _key);//TODO: move funciton to appropriate spot
void saveSequence(Options &_opt, vector<pair<double,string>> &_energyVector, vector<pair<double,vector<uint>>> &_energyStateVec, string _sequence, vector<uint> _state, double _energy);
void saveSequence(Options &_opt, RandomNumberGenerator &_RNG, map<vector<uint>, map<string,double>> &_stateEnergyMap, vector<pair<double,string>> &_energyVector, vector<pair<double,vector<uint>>> &_energyStateVec, string _sequence, vector<uint> _state, double _energy, ofstream &_out);
map<int,map<int,pair<uint, uint>>> setupRotamerPositionMap(System &_sys, vector<uint> _interfacialPositionsList);
void unlinkBestState(Options &_opt, vector<uint> &_bestState, vector<int> _linkedPositions, int _backboneLength);
bool convertStateMapToSequenceMap(System &_sys, vector<pair<double,vector<uint>>> &_energyStateVec, map<vector<uint>, map<string,double>> &_stateEnergyMap, map<string, map<string,double>> &_sequenceEnergyMap, vector<pair<string,vector<uint>>> &_sequenceStatePair, ofstream &_out);

/***********************************
 *sequence entropy functions
 ***********************************/
map<string,int> getAACountMap(vector<string> _seq);
double calcNumberOfPermutations(map<string,int> _seqAACounts, int _seqLength);
void interfaceAASequenceEntropySetup(string _seq, map<string,int> &_seqCountMap, double &_numberOfPermutations, vector<uint> _interfacialPositionsList);
void internalAASequenceEntropySetup(string _seq, map<string,int> &_seqCountMap, double &_numberOfPermutations, int _seqLength);
void sequenceEntropySetup(string _seq, map<string,int> &_seqCountMap, double &_numberOfPermutations, int _seqLength);
double calculateSequenceProbability(map<string,int> &_seqCountMap, map<string,double> &_entropyMap, double _numberOfPermutations);
//double getSequenceEntropyProbability(Options &_opt, string _sequence, map<string,double> _entropyMap);
//double getInterfaceSequenceEntropyProbability(Options &_opt, string _sequence, map<string,double> &_entropyMap, vector<uint> _interfacialPositionsList);
void calculateInterfaceSequenceEntropy(Options &_opt, string _prevSeq, string _currSeq, map<string,double> _entropyMap, double &_prevSEProb, double &_currSEProb, double &_prevEntropy, double &_currEntropy, double _bestEnergy, double _currEnergy, double &_bestEnergyTotal, double &_currEnergyTotal, vector<uint> _interfacePositionsList);
void calculateSequenceEntropy(Options &_opt, string _prevSeq, string _currSeq, map<string,double> _entropyMap, double &_prevSEProb, double &_currSEProb, double &_prevEntropy, double &_currEntropy, double _bestEnergy, double _currEnergy, double &_bestEnergyTotal, double &_currEnergyTotal);

// other functions
double getStandardNormal(RandomNumberGenerator& RNG);
void checkIfAtomsAreBuilt(System &_sys, ofstream &_err);
void addSequencesToVector(vector<pair<double,string>> &_energyVector, vector<string> &_allSeqs);

/***********************************
 *MonteCarlo functions
 ***********************************/
// Linked version of the state monte carlo
void stateMCLinked(System &_sys, SelfPairManager &_spm, Options &_opt, PolymerSequence &_PS, map<string, map<string,double>> &_sequenceEnergyMap, map<string,double> &_sequenceEntropyMap, vector<unsigned int> &_bestState, vector<string> &_seqs, vector<string> &_allSeqs, vector<pair<string,vector<uint>>> &_sequenceStatePair, vector<uint> &_interfacialPositionsList, vector<int> &_rotamerSampling, vector<vector<string>> &_linkedPos, RandomNumberGenerator &_RNG, ofstream &_sout, ofstream &_err);
void getEnergiesForStartingSequence(Options &_opt, SelfPairManager &_spm, string _startSequence, vector<unsigned int> &_stateVector, map<string, map<string, double>> &_sequenceEnergyMap, map<string, double> &_entropyMap);
// Unlinked version of the state monte carlo
void stateMCUnlinked(System &_sys, Options &_opt, PolymerSequence &_PS, map<string, map<string,double>> &_sequenceEnergyMap, map<string,double> &_sequenceEntropyMap, vector<unsigned int> &_bestState, vector<string> &_seqs, vector<string> &_allSeqs, vector<pair<string,vector<uint>>> &_sequenceStatePair, vector<uint> &_interfacialPositionsList, vector<uint> &_variablePositionsList, vector<int> &_rotamerSampling, vector<vector<string>> &_linkedPos, RandomNumberGenerator &_RNG, ofstream &_sout, ofstream &_err);
void getTotalEnergyAndWritePdbs(System &_sys, Options &_opt, map<string, map<string,double>> &_sequenceEnergyMap, string _sequence, vector<uint> _stateVec, vector<int> _rotamerSampling, RandomNumberGenerator &_RNG, int _seqNumber, PDBWriter &_writer, ofstream &_sout, ofstream &_err);
vector<uint> getAllInterfacePositions(Options &_opt, vector<int> &_rotamerSamplingPerPosition);
vector<uint> getInterfacePositions(Options &_opt, vector<int> &_rotamerSamplingPerPosition);
void getDimerSasaScores(System &_sys, vector<pair<string,vector<uint>>> &_sequenceStatePair, map<string, map<string,double>> &_sequenceEnergyMap);
void getSasaDifference(vector<pair<string,vector<uint>>> &_sequenceStatePair, map<string, map<string,double>> &_sequenceEnergyMap);
void getSasaForStartingSequence(System &_sys, string _sequence, vector<uint> _state, map<string, map<string,double>> &_sequenceEnergyMap);

#endif
