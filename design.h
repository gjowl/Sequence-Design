/**
 * @Author: Gilbert Loiseau
 * @Date:   2022/02/12
 * @Email:  gjowl04@gmail.com
 * @Filename: design.h
 * @Last modified by:   Gilbert Loiseau
 * @Last modified time: 2022/02/15
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
// ...
void c2Symmetry(AtomPointerVector & _apvA, AtomPointerVector & _apvB);
// moves the helices to the origin in 3D space (x=0, y=0, z=0)
void moveZCenterOfCAMassToOrigin(AtomPointerVector& _apV, AtomPointerVector& _axis, Transforms & _trans);
// transforms ...
void transformation(AtomPointerVector & _chainA, AtomPointerVector & _chainB, AtomPointerVector & _axisA, AtomPointerVector & _axisB, CartesianPoint & _ori, CartesianPoint & _xAxis, CartesianPoint & _zAxis, double _zShift, double _axialRotation, double _crossingAngle, double _xShift, Transforms & _trans);
// reads through geometry density file and randomly chooses a geometry for the dimer
void getGeometry(Options &_opt, RandomNumberGenerator &_RNG, vector<double> &_densities, ofstream &_out);

/***********************************
 *string output
 ***********************************/
// TODO: if possible, make some of these more multipurpose
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
// runs a greedy to quickly repack sidechains
void repackSideChains(SelfPairManager & _spm, int _greedyCycles);
// Code Samson made a while back that should get each active ID and set a mask for anything that isn't active
// allows for repacking side chains of only active ID...
std::vector < std::vector < bool > > getActiveMask (System &_sys);

/***********************************
 *define interface and rotamer sampling
 ***********************************/
// gets a vector of the rotamer level for each position on the protein
vector<int> getRotamerSampling(string _rotamerLevels);
//
vector<int> getLinkedPositions(vector<int> _rotamerSampling, int _interfaceLevel, int _highestRotamerLevel);
vector<uint> getVariablePositions(vector<int> &_interfacialPositions);
vector<vector<string>> convertToLinkedFormat(System &_sys, vector<int> &_interfacialPositions, int _backboneLength);
std::vector<pair <int, double> > calculateResidueBurial (System &_sys);
// Calculate Residue Burial for use in identifying the interfacial positions and output a PDB that highlights the interface
std::vector<pair <int, double> > calculateResidueBurial (System &_sys, Options &_opt, string _seq);
//TODO: change all of the original interfacePositions to variablePositions and the allInterfacePositions to interfacePositions
void defineInterfaceAndRotamerSampling(Options &_opt, PolymerSequence _PS, string &_rotamerLevels, string &_polySeq, string &_variablePositionString, string &_rotamerSamplingString, vector<int> &_linkedPositions, vector<uint> &_interfacePositions, vector<uint> &_variablePositions, vector<int> &_rotamerSamplingPerPosition, ofstream &_out, string _axis);

/***********************************
 *output file functions
 ***********************************/
// function to setup the output directory
void setupDesignDirectory(Options &_opt, string _date);
// function for outputting and writing and energy file
void outputEnergyFile(Options &_opt, string _interface, vector<string> _allDesigns);
// function that writes a config file for local geometric repacks by geomRepack.cpp
void makeRepackConfig(Options &_opt, string _sequence, string _designDir, string _designNumber, string _pdbPath, string _crdPath, map<string,double> _energyMap);
// function that writes a config file for running docking on our
void makeDockingConfig(Options &_opt, string _sequence, vector<uint> _state, string _pdbPath, map<string,double> _energyMap, vector<int> _rotamerSampling);
// function that writes and outputs the summarr, configuration, and energy files from this design run
void outputDesignFiles(Options &_opt, string _interface, vector<int> _rotamerSampling, vector<pair<string,vector<uint>>> _sequenceStatePair, map<string,map<string,double>> _sequenceEnergyMap, vector<double> _densities);

/***********************************
 *load rotamer functions
 ***********************************/
//load rotamers for a monomer
void loadMonomerRotamers(System &_sys, SystemRotamerLoader &_sysRot);
//load rotamers for dimer with different rotamer levels at each position
void loadRotamersBySASABurial(System &_sys, SystemRotamerLoader &_sysRot, Options &_opt, vector<int> &_rotamerSampling);
//load rotamers for non-interfacial positions
void loadRotamers(System &_sys, SystemRotamerLoader &_sysRot, string _SL);
//load rotamers for interfacial positions
void loadInterfacialRotamers(System &_sys, SystemRotamerLoader &_sysRot, string _SL, int _numRotamerLevels, vector<int> _interface);
//Uses rotamer sampling defined by SASA values to load rotamers by position
void loadRotamers(System &_sys, SystemRotamerLoader &_sysRot, Options &_opt, vector<int> &_rotamerSampling);

/***********************************
 *baseline energy helper functions
 ***********************************/
// calculates the self energies of a structure
vector<double> calcBaselineEnergies(System &_sys, int _seqLength);
// calculates the pair energies of a structure
vector<double> calcPairBaselineEnergies(System &_sys, int _seqLength);
// adds up all of the values in a vector<double> to get the total energy
double sumEnergyVector(vector<double> _energies);

/***********************************
 *calculate energies
 ***********************************/
// function to setup calculating the dimer energies of a vector<pair<string(sequence),vector<uint>(rotamer state)>>
void computeDimerEnergies(System &_sys, Options &_opt, map<string, map<string,double>> &_sequenceEnergyMap, vector<pair<string,vector<uint>>> &_sequenceStatePair, vector<int> _rotamerSamplingPerPosition, vector<vector<string>> &_linkedPos, RandomNumberGenerator &_RNG, ofstream &_sout, ofstream &_err);
// helper function for computeDimerEnergies: calculates energy for unlinked positions (different rotamers allowed at each position on opposite helices)
void computeDimerEnergy(System &_sys, Options& _opt, map<string,map<string,double>> &_sequenceEnergyMap, string &_sequence, vector<uint> &_stateVec, vector<int> &_rotamerSampling, vector<vector<string>> &_linkedPos, int _seqNumber, RandomNumberGenerator &_RNG, PDBWriter &_writer, ofstream &_sout, ofstream &_err);
// helper function for computeDimerEnergies: calculates energy for linked positions (same rotamer at each position on opposite helices)
void computeDimerEnergiesLinked(System &_sys, Options &_opt, map<string,map<string,double>> &_sequenceEnergyMap, vector<pair<string,vector<uint>>> &_sequenceStatePair, vector<int> &_rotamerSampling, vector<vector<string>> &_linkedPos, RandomNumberGenerator &_RNG, PDBWriter &_writer, ofstream &_sout, ofstream &_err);

// function to setup calculating the monomer energies of a vector<pair<string(sequence),vector<uint>(rotamer state)>>
void computeMonomerEnergies(Options &_opt, Transforms &_trans, map<string, map<string,double>> &_sequenceEnergyMap, vector<string> &_seqs, RandomNumberGenerator &_RNG, ofstream &_sout, ofstream &_err);
// helper function for computeMonomerEnergies: calculates energy for monomer without solvation energy
void computeMonomerEnergyNoIMM1(Options& _opt, map<string,map<string,double>> &_sequenceEnergyMap, string &_seq, RandomNumberGenerator &_RNG, ofstream &_sout, ofstream &_err);
// helper function for computeMonomerEnergies: calculates energy for monomer with solvation energy
void computeMonomerEnergyIMM1(Options& _opt, Transforms & _trans, map<string,map<string,double>> &_sequenceEnergyMap, string _seq, RandomNumberGenerator &_RNG, ofstream &_sout, ofstream &_err);


/***********************************
 *other helper functions
 ***********************************/
// goes through a list of ...
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
// gets a random position and chooses a random rotamer and applies it to both helices
void randomPointMutation(System &_sys, Options &_opt, RandomNumberGenerator &_RNG, vector<uint> _variablePositions, vector<string> &_ids);
// gets a random position and chooses a random rotamer for helix A and another random rotamer for helix B
void randomPointMutationUnlinked(System &_sys, Options &_opt, RandomNumberGenerator &_RNG, vector<uint> _variablePositions, vector<string> &_ids);
//TODO: are the below different
void checkSequenceVector(string &_newSeq, vector<string> &_seqs);
bool sameSequenceChecker(string &_newSeq, double &_newEnergy, vector<uint> &_state, vector<pair<double,string>> &_enerSeqPair, vector<pair<double,vector<uint>>> &_energyStateVec);
double getMapValueFromKey(map<string,double> &_map, string _key);//TODO: move funciton to appropriate spot
// save the sequence into a vector<pair<double(energy),string(sequence)>> that holds the most stable sequences from our monte carlo search
void saveSequence(Options &_opt, vector<pair<double,string>> &_energyVector, vector<pair<double,vector<uint>>> &_energyStateVec, string _sequence, vector<uint> _state, double _energy);
void saveSequence(Options &_opt, RandomNumberGenerator &_RNG, map<vector<uint>, map<string,double>> &_stateEnergyMap, vector<pair<double,string>> &_energyVector, vector<pair<double,vector<uint>>> &_energyStateVec, string _sequence, vector<uint> _state, double _energy, ofstream &_out);
//unlinks a state vector, replicating the state vector of the linked structure (i.e. for a sequence with 5 AAs and 5 rotamers each: linked: 0,1,2,3,4; unlinked: 0,1,2,3,4,0,1,2,3,4)
void unlinkBestState(Options &_opt, vector<uint> &_bestState, vector<int> _linkedPositions, int _backboneLength);
// converts the map of saved states and energies to saved sequences and energies for use through the rest of the code
bool convertStateMapToSequenceMap(System &_sys, vector<pair<double,vector<uint>>> &_energyStateVec, map<vector<uint>, map<string,double>> &_stateEnergyMap, map<string, map<string,double>> &_sequenceEnergyMap, vector<pair<string,vector<uint>>> &_sequenceStatePair, ofstream &_out);

/***********************************
 *sequence entropy functions
 ***********************************/
// counts the number of each AA in a sequence and outputs a map<string(AA),int(numAA)> ...
map<string,int> getAACountMap(vector<string> _seq);
// calculates the number of permutations possible for a sequence
double calcNumberOfPermutations(map<string,int> _seqAACounts, int _seqLength);
// sets up calculating sequence entropy for an interface (gets the AA counts for the interface
// and calculates the number of permutations for those AAs and the number of interfacial positions)
void interfaceAASequenceEntropySetup(string _seq, map<string,int> &_seqCountMap, double &_numberOfPermutations, vector<uint> _interfacialPositionsList);
// TODO: figure out if I just forgot to change these to interfacial for the starting sequence
// function that implements the above functions to calculate the sequence entropy of the interface
void calculateInterfaceSequenceEntropy(Options &_opt, string _prevSeq, string _currSeq, map<string,double> _entropyMap, double &_prevSEProb, double &_currSEProb, double &_prevEntropy, double &_currEntropy, double _bestEnergy, double _currEnergy, double &_bestEnergyTotal, double &_currEnergyTotal, vector<uint> _interfacePositionsList);
void internalAASequenceEntropySetup(string _seq, map<string,int> &_seqCountMap, double &_numberOfPermutations, int _seqLength);
void sequenceEntropySetup(string _seq, map<string,int> &_seqCountMap, double &_numberOfPermutations, int _seqLength);
double calculateSequenceProbability(map<string,int> &_seqCountMap, map<string,double> &_entropyMap, double _numberOfPermutations);
// function that implements the above functions to calculate the sequence entropy
void calculateSequenceEntropy(Options &_opt, string _prevSeq, string _currSeq, map<string,double> _entropyMap, double &_prevSEProb, double &_currSEProb, double &_prevEntropy, double &_currEntropy, double _bestEnergy, double _currEnergy, double &_bestEnergyTotal, double &_currEnergyTotal);

// other functions
// helper functions for computing monomer energy (actually not sure what it does yet)
double getStandardNormal(RandomNumberGenerator& RNG);
// helper function to ensure that all atoms are assigned coordinates (was having problems with this in the past and so I kept it in for troubleshooting)
void checkIfAtomsAreBuilt(System &_sys, ofstream &_err);
// adds sequences from the vector<pair<double,string>> energyVector to the vector of all sequences if it's not already in there
void addSequencesToVector(vector<pair<double,string>> &_energyVector, vector<string> &_allSeqs);

/***********************************
 *MonteCarlo functions
 ***********************************/
// stateMC: iterates through hundreds to thousands of sequences to find sequences that fit the given geometry
// Linked version
void stateMCLinked(System &_sys, SelfPairManager &_spm, Options &_opt, PolymerSequence &_PS, map<string, map<string,double>> &_sequenceEnergyMap, map<string,double> &_sequenceEntropyMap, vector<unsigned int> &_bestState, vector<string> &_seqs, vector<string> &_allSeqs, vector<pair<string,vector<uint>>> &_sequenceStatePair, vector<uint> &_interfacialPositionsList, vector<int> &_rotamerSampling, vector<vector<string>> &_linkedPos, RandomNumberGenerator &_RNG, ofstream &_sout, ofstream &_err);
// Unlinked version
void stateMCUnlinked(System &_sys, Options &_opt, PolymerSequence &_PS, map<string, map<string,double>> &_sequenceEnergyMap, map<string,double> &_sequenceEntropyMap, vector<unsigned int> &_bestState, vector<string> &_seqs, vector<string> &_allSeqs, vector<pair<string,vector<uint>>> &_sequenceStatePair, vector<uint> &_interfacialPositionsList, vector<uint> &_variablePositionsList, vector<int> &_rotamerSampling, vector<vector<string>> &_linkedPos, RandomNumberGenerator &_RNG, ofstream &_sout, ofstream &_err);
// adds the energies for the initial sequence accepted by the SelfPairManager (uses DeadEndElimination and/or SelfConsistentMeanField to get a sequence)
void getEnergiesForStartingSequence(Options &_opt, SelfPairManager &_spm, string _startSequence, vector<unsigned int> &_stateVector, map<string, map<string, double>> &_sequenceEnergyMap, map<string, double> &_entropyMap);
//
void getTotalEnergyAndWritePdbs(System &_sys, Options &_opt, map<string, map<string,double>> &_sequenceEnergyMap, string _sequence, vector<uint> _stateVec, vector<int> _rotamerSampling, RandomNumberGenerator &_RNG, int _seqNumber, PDBWriter &_writer, ofstream &_sout, ofstream &_err);
vector<uint> getAllInterfacePositions(Options &_opt, vector<int> &_rotamerSamplingPerPosition);
vector<uint> getInterfacePositions(Options &_opt, vector<int> &_rotamerSamplingPerPosition);
void getDimerSasaScores(System &_sys, vector<pair<string,vector<uint>>> &_sequenceStatePair, map<string, map<string,double>> &_sequenceEnergyMap);
void getSasaDifference(vector<pair<string,vector<uint>>> &_sequenceStatePair, map<string, map<string,double>> &_sequenceEnergyMap);
void getSasaForStartingSequence(System &_sys, string _sequence, vector<uint> _state, map<string, map<string,double>> &_sequenceEnergyMap);

#endif
