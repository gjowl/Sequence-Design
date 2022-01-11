#//To Do:
#//Read txt file
#//Parse out lines from text file(pull out residues)
#//Add in command to make lines between residues
#//Execute Pymol
#//Not too hard right??? :D

########################################################################
                          #Read Text File
########################################################################

#optimized by changing line color and putting residue list next to each distance
#can I think of ways to make the code shorter?

def code(*args):
    with open('%s' %args, 'r') as data:
	d = data.read()
	
#can now replace open file with any file in shell set to an arg1, arg2, etc.
   
#######################################################################
                #Parsing lines (Pt 2) with Python 2.7
#######################################################################i

#make sure you read the most correct version next time :P

    import string

    pre = d.splitlines()
#splits the data by line
    for x in enumerate(pre, 1):
        print(x)

    
    joined = ' '.join(pre)
#reverts the data from a list to a workable script
#here is where we need to do it by alphabet
    
    noletters = joined.translate(None, string.ascii_uppercase)
#removes uppercase letters

    nonumbers = joined.translate(None, string.digits)
#removes numbers

    number = noletters.translate(None, string.punctuation)
#removes punctuation

    letter = nonumbers.translate(None,string.punctuation)
#removes punctuation

    residue = number.split(' ')
#now prints out a list of each residue with just numbers

    resilet = letter.split(' ')
#should print out list of residue just letters

    residuepair1 = residue[0:2]
#will split up pairs of the residues

#def chain(residue):
#    chain1, chain2 = [], []
#    for x in residue:
#        chain1.append(x)
#        chain1, chain2 = chain2, chain1
#    return chain1, chain2
#
#print(chain(residue))
##will give individual but can't rename them
##could probably split just need to find how

    chain1 = residue[0:][::2]
    chain2 = residue[1:][::2]
#so now have all numbers in separate lists separated by chain
    letters1 = resilet[0:][::2]
    letters2 = resilet[1:][::2]

#########################################################################
                                #Pymol
#########################################################################                             
#need to insert commands from pymol here so that it will read it in pymol
    from pymol import cmd

#cmd.select('resa',"chain A and resi %s and name CA" %residue[0]) 
#cmd.select('resb',"chain A and resi %s and name CA" %residue[1])
#
#cmd.distance('one', 'resa', 'resb')
#works! now need to run a for loop so that it does all of it
#...but what...?
#want to iterate through the numbers in the chains and add a "counter" number to it if duplicate to make easier for selections
    
    
    def selector(a, b):
        count=1
        for number, letter in zip(a, b):
            cmd.select('res%s%s%d' %(letter, number, count),"chain %s and resi %s and name CA" % (letter, number))
            count += 1

    selector(chain1, letters1)
    selector(chain2, letters2)
                        
#    for number, letter in zip(chain1, letters1):
#        cmd.select('res%s%s' %(letter, number),"chain %s and resi %s and name CA" %(letter, number))
#        [count]='res%s%s'%(letter,number)
#        count += 1
#    
#    for number, letter in zip(chain2, letters2):
#        cmd.select('res%s%s' %(letter, number),"chain %s and resi %s and name CA" %(letter, number))
#        [count]='res%s%s'%(letter,number)
#        count += 1
#gives all numbers of residues WOW, also added to pick chains! 
#next want a function that outputs different number for '%d' so each line has different name


    def dist(a, b, c, d):
        cmd.distance("dist%d" %dist.counter, 'res%s%s%d' %(c, a, dist.counter), 'res%s%s%d' %(d, b, dist.counter))
        r=cmd.distance("dist%d" %dist.counter, 'res%s%s%d' %(c, a, dist.counter), 'res%s%s%d' %(d, b, dist.counter))
        cmd.hide('labels', "dist%d" %dist.counter)
        if r <= 15.0:
            cmd.set('dash_color', 'marine', 'dist%d' %dist.counter)
        else:
            cmd.set('dash_color', 'red', 'dist%d' %dist.counter)
        cmd.set('dash_gap', 0)
        cmd.set('dash_width', 4)
        print("Distance %d: %f; %s,%s %s,%s" %(dist.counter, r, c, a, d, b))    
        dist.counter += 1 
    dist.counter = 1 
#add in %letters to see if put in?
#counts up everytime the function is used and gives each that number name!
#also hides all labels
#now changes color of lines if distance more than 10.0

    for a, b, c, d in zip(chain1, chain2, letters1, letters2):
        dist(a, b, c, d)
#it works :D
#and gives out residue printed out next to distance!
   
    cmd.hide('lines')
    cmd.show('cartoon')
#can show cartoon and hide lines from script


#also hides all labels
#now...is it possible to make a for loop for the list of residues?
#but with repeats makes it a bit harder
#for x, y in number:
#    def dist(x, y):
#        dist.counter += 1
#        cmd.distance('%d' %dist.counter, 
#try to make a for loop that pulls up 'res%s' and then use number1/2 to combine
#maybe index values?

# for finding best model and inputing in file#grep -ri best ./ > /tmp/FtsK_energies.tsv

cmd.extend("code", code)

