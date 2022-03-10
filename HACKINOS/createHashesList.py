import hashlib
	
nameOfFile = "reverse_shell.php"
for i in range(1,100):
	hashedFileName = hashlib.md5((nameOfFile+str(i)).encode()).hexdigest()
    print(hashedFileName+".php")