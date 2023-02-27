from pymol import cmd
import sys, os

# get current working directory
cwd = os.getcwd()

# read in the pdbs from the command line
pdb1 = sys.argv[1]
pdb2 = sys.argv[2]

# get the pdb names without the extension and after the last slash
pdb1Name = os.path.splitext(os.path.basename(pdb1))[0]
pdb2Name = os.path.splitext(os.path.basename(pdb2))[0]

# open the pymol gui
cmd.reinitialize()

# load the pdbs and name them
cmd.load(pdb1, pdb1Name)
cmd.load(pdb2, pdb2Name)

# get the CA atoms
cmd.select('ca1', pdb1Name+' and name ca')
cmd.select('ca2', pdb2Name+' and name ca')

# get the alignment
print(cmd.align('ca1', 'ca2', object="alignment"))

# save the pymol session
cmd.save(f'{cwd}/aligned.pse')

