#1 uppercase character
#1 digit
#One of the words in my old bands name.

# e.g. for viable password ---> D8The

Ricks_Band = "The Flesh Curtains".split()

for c in range(65,90):
    for n in range(10):
        for word in Ricks_Band:
            print(chr(c) + str(n) + word)