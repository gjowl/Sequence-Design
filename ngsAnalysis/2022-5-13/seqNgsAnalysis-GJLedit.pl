#!/usr/bin/perl
#This program takes a NGS file in the form of FASTQ, analyzes it for quality
#and outputs the counts of each sequence in the run. 
#TODO: If you use the correct GpA/G83I sequence in the future...yay for you. Change the reference sequence at the bottom. ='[

use warnings;
use strict;
use Getopt::Long;

my $refFile;
my $seqFile;
my $direction;
 
GetOptions(
    "refFile=s" => \$refFile,
    "seqFile=s" => \$seqFile,
    "direction=i" => \$direction)
or die ("perl ngsAnalysis.pl [--refFile <>] [--seqFile <>] [--direction <1|2>]\n");

#Translation hashes
my %geneticCode = (
	"UUU" => "F",
	"UUC" => "F",

	"UUA" => "L",
	"UUG" => "L",
	"CUU" => "L",
	"CUC" => "L",
	"CUA" => "L",
	"CUG" => "L",

	"AUU" => "I",
	"AUC" => "I",
	"AUA" => "I",

	"AUG" => "M",

	"GUU" => "V",
	"GUC" => "V",
	"GUA" => "V",
	"GUG" => "V",

	"UCU" => "S",
	"UCC" => "S",
	"UCA" => "S",
	"UCG" => "S",
	
	"CCU" => "P",
	"CCC" => "P",
	"CCA" => "P",
	"CCG" => "P",

	"ACU" => "T",
	"ACC" => "T",
	"ACA" => "T",
	"ACG" => "T",
	
	"GCU" => "A", 
	"GCC" => "A",
	"GCA" => "A",
	"GCG" => "A",

	"UAU" => "Y",
	"UAC" => "Y",

	"UAA" => "-",
	"UAG" => "-",
	"UGA" => "-",
	
	"CAU" => "H",
	"CAC" => "H",
	
	"CAA" => "Q",
	"CAG" => "Q",
	
	"AAU" => "N",
	"AAC" => "N",

	"AAA" => "K",
	"AAG" => "K",

	"GAU" => "D",
	"GAC" => "D",
	
	"GAA" => "E",
	"GAG" => "E",
	
	"UGU" => "C",
	"UGC" => "C",
	
	"UGG" => "W",

	"CGU" => "R",
	"CGC" => "R",
	"CGA" => "R",
	"CGG" => "R",
	"AGA" => "R",
	"AGG" => "R",

	"AGU" => "S",
	"AGC" => "S",
	
	"GGU" => "G",
	"GGC" => "G",
	"GGA" => "G",
	"GGG" => "G",
);

my %basePairs = (
	"A" => "U",
	"U" => "A",
	"C" => "G",
	"G" => "C",
);

#Print Info
print "$seqFile\t$direction\n";

#Load reference sequences
open (FILE, $refFile) or die "Can't open file\n";
my @ref = <FILE>;
close(FILE);
my %reference;
foreach my $refSeq(@ref){
	chomp $refSeq;
	# the below splits lines and adds to a way of identifying information 
	my @line = split ',', $refSeq;
	my $ID = $line[0] . "\t"; 
	$reference{$line[1]} = $ID;
}


#Print the hash containing the sequences
#foreach my $key (keys %reference){
#	print "$key\t$reference{$key}\n";
#}

#Choose whether it is a fwd or rvs sequence
#These are the primers from amplifying out of the plasmid
my ($fPrimer, $rPrimer, $offset);
if ($direction == 1){
	$fPrimer = "GGCTCCAAACTTGGGGAATCG";
	$rPrimer = "CCTGATCAACCCAAGCCAATCC";
	$offset = 21;
} else {
	$fPrimer = "GGATTGGCTTGGGTTGATCAGG";
	$rPrimer = "CGATTCCCCAAGTTTGGAGCC";
	$offset = 22;
}

open (FILE, $seqFile) or die "Can't open $seqFile\n";
my @lines = <FILE>;
close(FILE);
my $numLines = scalar @lines;
my $numSeqs = $numLines / 4;

#Cutoff for the number of seqs that we will analyze 
#Starter is 0.01%
#my $cutOff = $numSeqs * 0.001;
my $cutOff = 10;
print "Number of Sequences: $numSeqs\tCutoff: $cutOff\n";

#Group value is the line. Each entry has 4 lines:
#Label
	#@M01987:419:000000000-BKRPV:1:1101:14644:1644 1:N:0:TAGACCGA+TAGACCGA
#Sequence
	#AAGGTGGGCTCCAAACTTGGGGAATCGAGCTAGCCTCATTATTTTTGGGGTGATGGCTGGTGTTATTGGAACGATCCTGATCAACCCAAGCCAATCCTTCCAGATCGGAAGAGCACACGTCTGAACTCCAGTCACTAGACCGAATCTCGTA
#Something....
	#+
#Q Codes
	#1>>?AB?@>FAAF1DGGGFFCCCFHHFCFFF1FFGHHBGGBGHHHHCCCCFEEHFGFHGCHGHGBGHHGFEGECGHFHHBGHFGHFECCAFGEFGGFHHH0BFFGHGCCEEEFHHHGFGHHHGGHHHHHHFHHGHHBGFHHG?/F/GHFF.
my $groupValue = 0;
my $sequence;
my %sequences;
my %proteinSeqs;
my $poorSeq = 0;
my $noStart = 0;
my $noEnd = 0;

for (my $i = 0; $i < $numLines; $i++){
	chomp $lines[$i];
	#P = the estimated probability of incorrect base in a seq (Lower is better)
	#Q = the Q factor given by the sequencing results (Higher is better)
	#P = 10^(-Q/10)
	my ($Q, $P, $eIncorrect, $tm);
	if ($groupValue == 1){ #store full DNA sequence
		$sequence = $lines[$i];
		$groupValue++;
		next;
	} elsif ($groupValue == 3){ #caclulate P
		for my $c (split //, $lines[$i]) {
			$Q = ord($c)-33;
			$P = 10**(-$Q/10);
			$eIncorrect += $P;
		}
		$groupValue = 0;
		if ($eIncorrect > 1){
			$poorSeq++;
			next;
		}
	} else {
		$groupValue++;
		next;
	}
	my $j = index $sequence, $fPrimer; 
	my $k = index $sequence, $rPrimer;
	
	
	#Crop good sequences to inbetween the primers
	if ($j == -1){
		$noStart++;
		next;
	}
	$j = $j + $offset;	
	if ($k != -1){
		$tm = substr($sequence, $j, ($k-$j));
	} else {
		$noEnd++;
		next;
	}

#	print "$sequence\t$tm\t";
#	print "$tm\t";

	#Convert DNA to protein
	my $protein = &Conversion($tm);
	#print "$i\n";
	#print "$j\n";
	#print "$k\n";
	#print "$sequence\n";
	#print "$tm\n";
	#print "$protein\n";

	if (substr($protein, 0, 2) ne "AS"){
		$noStart++;
		next;
	} elsif (substr($protein, -1) ne "L"){
		$noEnd++;
		next;
	} else {
		#print "$tm\t";
		$protein = substr($protein, 2);
		$protein = substr($protein, 0, -1);
	}
	if (exists $proteinSeqs{$protein}){
		$proteinSeqs{$protein}++;
	} else {
		$proteinSeqs{$protein} = 1;
	}
}

#Print out fails
my $goodSeqs = $numSeqs - $poorSeq - $noStart - $noEnd;
my $goodPercent = $goodSeqs / $numSeqs;
print "TotalSeqs\tPoorSeqs\tNoStart\tNoEnd\tGoodSeqs\tPercent\n";
print "$numSeqs\t$poorSeq\t$noStart\t$noEnd\t$goodSeqs\t$goodPercent\n";
#Sort amino acid sequences
for my $aa (sort {$proteinSeqs{$b} <=> $proteinSeqs{$a} }keys %proteinSeqs){
	if ($proteinSeqs{$aa} > $cutOff){ #remove seqs less than cutoff
		#percent of this seq in total
		my $percentage = $proteinSeqs{$aa} / $numSeqs ;
		print "$aa\t$proteinSeqs{$aa}\t$percentage\t";
		#Find reference label
		if (exists $reference{$aa}){
			print "$reference{$aa}\n";
		} elsif ($aa eq "LIIFGMAGVIGT"){
			print "0\tP02724\tGLPA_HUMAN\t75\tWT\tN/A\n";
		} elsif ($aa eq "LIIFGMAIVIGT"){
			print "0\tP02724\tGLPA_HUMAN\t75\tG83I\t83\n";
		} else {
			print "Unknown\n";
		}
	}
}


#Translate
sub Conversion {
	my $testSeq = $_[0];
	
	#convert all sequences to standard Uracil (RNA) format	
	if (index ($testSeq, "T") != -1){
		$testSeq =~ s/T/U/gi;
	};
	#Reverse complement seq
	my $threeto5 = reverse $testSeq;
	my $reverse = "";
	my $aminoAcids;
	for (my $j = 0; $j < length($testSeq); $j++){
		my $base = substr($threeto5, $j,1);
		my $complement = $basePairs{$base};
		$reverse = $reverse . $complement;	
	};
	
	#Translate both directions
	if ($direction == 1){
		my $i = 1;
		$aminoAcids = &Translate($testSeq, $i);
	} else {
		my $k = 1;
		$aminoAcids = &Translate($reverse, $k);
	}
	return $aminoAcids
}
sub Translate{
	#translate the DNA
	#move down the string
	my $aminoAcids = "";
	my $dnaSeq = $_[0];
	my $sequenceLength = length($dnaSeq);
	my $startPos = $_[1];
	my $orf = 0;
	my $i = $startPos;
	#move down the string by 3s (codons)
	for ($i = $startPos; $i < $sequenceLength ; $i = $i+3) {
		my $begin = "M";
		my $stop = "-";
		my $end = " End of gene \n";
		my $startIndicator = "{";
		my $endIndicator = "}";
		my $codon = substr($dnaSeq, $i,3);
		if (length($codon) ne 3){
			last;
		}
		my $acid = $geneticCode{$codon};
		#while the acid isn't stop, run the translations
		if ($acid eq $begin && $orf == 0){
			$orf = 1;
			$aminoAcids = $aminoAcids . $acid;
		}elsif ($acid ne $stop) {
		#	print "$i $codon $acid \n";
			$aminoAcids = $aminoAcids . $acid;
		}elsif ($acid eq $stop && $orf == 0){
			$aminoAcids = $aminoAcids . $stop;
		
		}elsif ($acid eq $stop && $orf == 1){
			$orf = 0;
			$aminoAcids = $aminoAcids . $stop;
		} 
	}
	return $aminoAcids;
};


