import pandas as pd
import random as rand
from utilityFunctions import *
from dnachisel.biotools import reverse_translate

#Functions
def getPrimerSet(dfFwd, dfRvs, row):
    fwdPrimer = dfFwd['Fwd'][row-1]
    revPrimer = dfRvs['Rvs'][row-1]
    return fwdPrimer, revPrimer

def getRandomDNAEnd(length):
    randSeq = ""
    DNA = ['g', 'a', 't', 'c']
    while len(randSeq) < length:
        randSeq = randSeq+rand.choice(DNA)
    return randSeq

def getCHIPFile(df, dfFwdP, dfRevP, gpaSeq, g83ISeq, cut1, cut2, randomDNALength):
    dictOutput = {}
    colNames = ['Segment Number', 'TM Sequence', 'DNA Sequence']
    addColumnsToDictionary(dictOutput, colNames)
    for segmentNum in df['SegmentNumber'].unique():
        dfSegment = df[df['SegmentNumber'] == segmentNum]
        sequenceList = dfSegment["Sequence"]
        fwd, rvs = getPrimerSet(dfFwdP, dfRevP, segmentNum)
        # For every sequence, make a random string that is 90% different from primers and cutSite
        for sequence in sequenceList:
            randomDNAEnd = getRandomDNAEnd(randomDNALength)
            while randomDNAEnd.find(fwd) is True or randomDNAEnd.find(rvs) is True:
                randomDNAEnd = getRandomDNAEnd(randomDNALength)
            DNASeq = reverse_translate(sequence[0:17])
            while DNASeq.find(fwd) is True or DNASeq.find(rvs) is True:
                DNASeq = reverse_translate(sequence[0:17])
                #TODO: why did I add this TT and AC? Should it have been ACA?
            seqForChip = fwd + cut1 + DNASeq + 'TT' + cut2 + rvs + randomDNAEnd
            dictOutput['DNA Sequence'].append(seqForChip)
            dictOutput['Segment Number'].append(segmentNum)
            dictOutput['TM Sequence'].append(sequence[0:18])
        while gpaSeq.find(fwd) is True or gpaSeq.find(rvs) is True:
            gpaSeq = reverse_translate(gpaSeq)
        while g83ISeq.find(fwd) is True or g83ISeq.find(rvs) is True:
            g83ISeq = reverse_translate(g83ISeq)
        gpaDNASeq = fwd + cut1 + gpaSeq + 'AC' + cut2 + rvs + randomDNAEnd
        g83IDNASeq = fwd + cut1 + g83ISeq + 'AC'+ cut2 + rvs + randomDNAEnd
        i=0
        # At end of segment, add in the control sequences with a function
        for i in range(0,5):
            dictOutput['DNA Sequence'].append(gpaDNASeq)
            dictOutput['DNA Sequence'].append(g83IDNASeq)
            dictOutput['Segment Number'].append(segmentNum)
            dictOutput['Segment Number'].append(segmentNum)
            dictOutput['TM Sequence'].append(gpaSeq)
            dictOutput['TM Sequence'].append(g83ISeq)
            i+=1
    outputDf = pd.DataFrame.from_dict(dictOutput)
    return outputDf