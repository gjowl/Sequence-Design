'''
File: /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/figureMaking/code/potentialHBondCounter.py
Project: /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/figureMaking/code
Created Date: Thursday February 8th 2024
Author: loiseau
-----
Description:
This script will count the number of potential hydrogen bonds in a protein. It will take in a pdb file,
find any oxygen atoms for desired amino acids on a backbone, and then output the number of potential hydrogen bonds
in the protein. 
-----
'''

from pymol import cmd
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# TODO:
# 1. Take functions from other scripts to read in pdb
# 2. Identify the given amino acids and their oxygen atoms from the pdb
# 3. Count the number of potential hydrogen bonds in the protein (using some distance cutoff for interhelical hydrogen bonds)
# 4. Output the number of potential hydrogen bonds in the protein
# 5. If time, could also try to change rotamers of the amino acids to see if the number of potential hydrogen bonds changes