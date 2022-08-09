import sys
import os
import random
import argparse
from functions import *
"""
Run as:
    python3 generateGeomCsv.py 

This code is used to generate csvs for a condor design run. You can input different numbers
for the spread of each geometry and the number of geometries to generate. The output will
be a csv file with the following columns:
xShift,crossingAngle,negAngle,axialRotation,zShift
"""
# get the current directory

# parse the command line arguments
parser = argparse.ArgumentParser(description='Generate a csv file for a condor design run.')
parser.add_argument('-n', '--numGeoms', type=int, default=10, help='The number of geometries to generate.')
parser.add_argument('-outputDir', '--outputDir', type=str, default=os.getcwd(), help='The output directory.')
parser.add_argument('-xShift', '--xShift', type=float, default=6.3, help='The starting xShift of the geometry.')
parser.add_argument('-xSpread', '--xSpread', type=float, default=1, help='Added to the start xShift of the geometry.')
parser.add_argument('-crossingAngle', '--crossingAngle', type=float, default=-40, help='The starting crossing angle of the geometry.')
parser.add_argument('-angSpread', '--angSpread', type=float, default=10, help='Added to the start crossing angle of the geometry.')
parser.add_argument('-axialRotationS', '--axialRotationStart', type=float, default=0, help='The starting axial rotation of the geometry.')
parser.add_argument('-axialRotationE', '--axialRotationEnd', type=float, default=100, help='The end axial rotation of the geometry.')
parser.add_argument('-zShiftS', '--zShiftStart', type=float, default=0, help='The starting zShift of the geometry.')
parser.add_argument('-zShiftE', '--zShiftEnd', type=float, default=6, help='The starting zShift of the geometry.')
parser.add_argument('-filename', '--filename', type=str, default='geom', help='The name of the csv file to generate.')
args = parser.parse_args()

#MAIN
csvRows = []
# loop to generate the geometries
generateGeometries(args, csvRows)

# TODO: if I wanted to, I could also get the density for each here and add it to the row
writeCsv(csvRows, args)
