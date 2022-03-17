# @Author: Gilbert Loiseau
# @Date:   2021-12-19
# @Filename: pythonTips.py
# @Last modified by:   Gilbert Loiseau
# @Last modified time: 2021-12-19
"""
Videos that I got some of these examples from:
25 nooby Python habits: https://www.youtube.com/watch?v=qUeud6DvOWI&ab_channel=mCoding
"""
# Python Programming Tips and Shortcuts


# Checking for type
"""
If you want to write a check for a type of variable (i.e. string is a string and not an integer/double/float/dict/etc.),
do not use the == . This isn't always clear, especially for a subtype of a type (Liskov rule?). Instead, use isinstance(type, typeToCompare)
"""
# Example:

Point = namedtuple('Point', ['x', 'y'])
p = Point(1,2)
if p == tuple:
    print("a tuple")
else:
    print("not a tuple")
else if isinstance(p, tuple):
    print("it's a tuple")
else:
    print("it's not a tuple")

"""
If you come from a different coding language such as C++ or Java, it is common to use == to check for identity/equality.
Instead, just use is.
"""

#Looping
"""
In other languages, pulling out elements from a list/vector/data structure is usually done by using the index to pull out the element.
However, in python there are much easier ways to do this that make your code more readable.
"""

#Other Languages
a = [1, 2, 3]
for i in range(len(a)):
    num = a[i]
    print(num)

#python
for num in a:
    print(num)

#get index and element using enumerate
for i, num in enumerate(a):
    indexColonValue = i + ": " + num
    print(indexColonValue)

#For multiple object, other language
a = [1, 2, 3]
b = [4, 5, 6]
for i in range(len(b)):
    num1 = a[i]
    num2 = b[i]
    print("Num1: " + num1)
    print("Num2: " + num2)

#get both elements using zip
for num1, num2 in zip(a, b):
    print("Num1: " + num1)
    print("Num2: " + num2)

#using zip and enumerate to get get both index and elements
for i, (num1, num2) in enumerate(zip(a, b)):
    indexColonValue1 = i + ": " + num1
    indexColonValue2 = i + ": " + num2
    print(indexColonValue1)
    print(indexColonValue2)

"""
The information for looping above also applies to dictionaries!
"""
#I think this could be a fun coding example: give a list of words and see if people can make sentences using just those
# - could also make them randomize the upper and lowercase, make some words upper and lower first letter, upper and lower middle letters, etc.

d = {"I":'Me', "Like": 'Love', "Turtles": 'Owls'}
#When looping through a dictionary, you can easy pull out a key
for key in d:
    val = d[key]
    print(key)
    print(val)
#But if you really want the value, you can easily get that without the above hassle
for key, val in d.items():
    print(key)
    print(val)

#TODO: look into and elaborate
"""
Logging errors: python has a very convenient logging module that you can import and setup for outputs that aid in debugging.
"""
def print_vs_logging():
    logging.debug("debug info")
    logging.info("random info")
    logging.error("error info")

level= logging.DEBUG
fmt = '[%(levelname)s] %(asctime)s - %(message)s'
logging.basicConfig(level=level, format=fmt)

"""
learn how to package code and install into the environment, so I don't have to make sure all things are fonud in the same directory
"""

#Example: package utility file code so it's easy to pull from anywhere
#If you aren't going to use many functions from the file, might be good to just import one function from there to not clutter namespace with variables
from ...package.utility import *

"""
use pep8 style guide as a common practice to help make your code readable to others
"""
#Non-pep8:

#pep8
