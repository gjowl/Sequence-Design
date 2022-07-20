import random
# loop to generate geometries from arguments
def generateGeometries(args, rows):
    # variables
    # xShift
    xShiftStart, xShiftEnd = args.xShift, args.xShift+args.xSpread
    # crossingAngle
    crossAngleStart, crossAngleEnd = args.crossingAngle, args.crossingAngle+args.angSpread
    # check if angle is negative
    if crossAngleStart < 0:
        negAngle = True
    else:
        negAngle = False
    # axialRotation
    axialRotStart, axialRotEnd = args.axialRotationStart, args.axialRotationEnd
    # zShift
    zShiftStart, zShiftEnd = args.zShiftStart, args.zShiftEnd
    for i in range(args.numGeoms):
        # get a random decimal between xShiftStart and xShiftEnd
        xShift = round(random.uniform(xShiftStart, xShiftEnd), 3)
        # get a random decimal between crossAngleStart and crossAngleEnd
        crossingAngle = round(random.uniform(crossAngleStart, crossAngleEnd), 3)
        # get a random decimal between axialRotStart and axialRotEnd
        axialRotation = round(random.uniform(axialRotStart, axialRotEnd), 3)
        # get a random decimal between zShiftStart and zShiftEnd
        zShift = round(random.uniform(zShiftStart, zShiftEnd), 3)
        # save the values as a row in the csv
        row = [i, xShift, crossingAngle, negAngle, axialRotation, zShift]
        # add the row to the list
        rows.append(row)

# write the csv
def writeCsv(rows, args):
    # open the csv file
    filename = args.filename + '.csv'
    with open(filename, 'w') as f:
        # write the header
        f.write('runNumber,xShift,crossingAngle,negAngle,axialRotation,zShift\n')
        # write the rows
        for row in rows:
            f.write(','.join(str(x) for x in row) + '\n')