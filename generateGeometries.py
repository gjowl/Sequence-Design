#This script is meant to create a list of geometries to be used to test for computational design

########################################################################
#                      WRITE EXECUTABLE FILE
########################################################################

dist = 8.2
ang = 55
axrot = 35
z = 1.2

distinc = 0.5
anginc = 5
axrotinc = 5
zinc = 0.2

dirName = '/data02/gloiseau/Sequence_Design_Project/interhelicalCoordinates/membraneProteins/pdbs/opm_pdbs/pdbs/'

executefile = open('/exports/home/gloiseau/submit_geometries_neg_2.txt', 'w')

args = 'arguments = "'
config = '--config $(configFile)'
run = ' --runNumber '
xShift = ' --xShift '
crossingAngle = ' --crossingAngle '
axialRotation = ' --axialRotation '
zShift = ' --zShift '
outputdir = ' --outputdir $(outputdir)/'
p = '"'

########################################################################
#               UNOPTIMIZED WAY TO GET MOST GEOMETRIES
########################################################################
count = 0
for d in range(0, 4):
    dist1 = dist + distinc*d
    dist1 = round(dist1, 2)
    for a in range(0, 8):
        ang1 = ang + anginc*a
        for x in range(0, 5):
            axrot1 = axrot + axrotinc*x
            for y in range(0, 19):
                z1 = z + zinc*y
                z1 = round(z1, 2)
                executefile.write(args)
                executefile.write(config)
                executefile.write(run)
                executefile.write(str(count))
                executefile.write(xShift)
                executefile.write(str(dist1))
                executefile.write(crossingAngle)
                executefile.write(str(ang1))
                executefile.write(axialRotation)
                executefile.write(str(axrot1))
                executefile.write(zShift)
                executefile.write(str(z1))
                executefile.write(p)
                executefile.write('\n')
                executefile.write('queue')
                executefile.write('\n')
                count += 1

executefile.close()

#arguments = "--config $(configFile) --runNumber 54 --crossingAngle 25 --axialRotation 55 --zShift 3.6 --xShift 6 --varPos 0 0 0 0 0 0 0 0 1 0 0 0 0 1 0 0 0 0"
print("Finished!")
