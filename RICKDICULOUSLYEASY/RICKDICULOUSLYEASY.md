Source: https://www.vulnhub.com/entry/rickdiculouslyeasy-1,207/  
Target: 10.0.0.26  
Diffuculty: Easy

**In order to complete this CTF we must get all 130 points, so we need to find every flag until it adds up to 130.**

## NMAP

> nmap -sS -sV -p- 10.0.0.24

![image](https://user-images.githubusercontent.com/76552238/157470893-78ec3c9d-034e-4926-9e81-924f2b068ce2.png)

The NMAP scan shows there are 7 open ports.
## FTP 

Since we have any credentials, we can't log into FTP, but if enabled there is an option
in FTP which allows to enter as an anonymous user and thuse requires no password.

> ftp 10.0.0.26

![image](https://user-images.githubusercontent.com/76552238/157472285-0b0f0b93-8488-45b2-9497-b9ce2579cb64.png)

![image](https://user-images.githubusercontent.com/76552238/157472418-8977783d-6734-47ac-a750-87a14eea9baa.png)

And It Worked...  
We can get our first flag.

FLAG{Whoa this is unexpected} - 10 Points

The directory 'pub' is empty.

## PORT 13337

NMAP doesn't tell us what service is running on this port, but we can access it using the 'telnet' command.

> telnet 10.0.0.26 13337

![image](https://user-images.githubusercontent.com/76552238/157473179-41b9c423-2b27-43db-9e7f-d17b82e36260.png)

We get another flag.

## PORT 60000

Same story here.

> telnet 10.0.0.26 60000

![image](https://user-images.githubusercontent.com/76552238/157473695-25e7fc6d-96f0-41be-b73d-7e34b3002324.png)

## PORT 9090 | ZEUS ADMIN

Port 9090 is running 'zeus-admin'. Going to http://10.0.0.26:9090 it displays another flag.

![image](https://user-images.githubusercontent.com/76552238/157474248-8a714df9-ba14-4d3a-931c-c5f44fe89a80.png)

## HTTP

Going into the http://10.0.0.26, there are no hyperlinks ,no buttons and no comments.
Let's brute force the directories.

> gobuster dir -u http://10.0.0.26 -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt -x txt

![image](https://user-images.githubusercontent.com/76552238/157474957-a14efc55-8748-4dfc-a95a-08836e80751b.png)

http://10.0.0.22/passwords/ holds another flag.

![image](https://user-images.githubusercontent.com/76552238/157475092-c2ef1acc-b636-407f-a9fa-2810f8d957e3.png)

There is also a file called 'passwords.html'.

![image](https://user-images.githubusercontent.com/76552238/157475217-a27a9046-c927-4845-a1e8-1b31fc897e1c.png)

There is a comment that holds a password.

![image](https://user-images.githubusercontent.com/76552238/157475412-b3f2cf52-e710-4722-ab7c-2f4ac88211fd.png)

http://10.0.0.26/robots.txt has another message from Rick.

![image](https://user-images.githubusercontent.com/76552238/157475606-0aff170a-e571-4926-9a41-5d157e9dcd32.png)

The directory 'cgi-bin' in web servers is responsible for executing external programs.
cgi-bin/root_shell.cgi doesn't have any useful information.

Going into /cgi/bin/tracertool.cgi we have an input box. When we enter an IP, we get that output of the traceroute command running the machine hosting the web server. Let's see if it is vulnerable to RCE (Remote Command Execution). Let's test this by entering ';', we should be able to run our own commands on the machine.

> ; ls -l

![image](https://user-images.githubusercontent.com/76552238/157477143-db802eb3-afd4-48aa-9707-c80020f36304.png)

## REVERSE SHELL

> Local Machine:

![image](https://user-images.githubusercontent.com/76552238/157477415-23f74864-e050-48c9-afd5-9070b374accd.png)

> Target Machine:

![image](https://user-images.githubusercontent.com/76552238/157477538-6b6fc328-ef26-45f4-9707-dc14a584a21e.png)

![image](https://user-images.githubusercontent.com/76552238/157477723-363ef136-5119-49f3-b491-1e1874d30918.png)

Using the "whoami" command we can we are the user 'apache'.
Trying to use cat to read the /etc/passwd file does not seem to work, instead it prints an ascii banner of a cat.  

> cat /etc/passwd | grep /bin/bash

![image](https://user-images.githubusercontent.com/76552238/157488913-66806f98-4057-4084-bf2d-2874d9f49043.png)

We can try using the command 'tail' to read the /etc/passwd file.  

> tail /etc/passwd | grep /bin/bash

![image](https://user-images.githubusercontent.com/76552238/157488819-40a9f850-d2d4-497c-bf38-a53851942b42.png)

## PORT 22222 | SSH

We can try brute forcing the SSH login using the usernames we found and the password 'winter'.  

> hydra -L users.txt -p '
' ssh://10.0.0.26:22222 -IV

![image](https://user-images.githubusercontent.com/76552238/157479594-11bbfad7-190a-46d6-86ee-8ad1cddaaf1c.png)

Ah get it , winter summer, never mind.
After loggin to the machine we can get another flag.

![image](https://user-images.githubusercontent.com/76552238/157479930-ee530d1e-05ef-4610-bbd3-3de597964c77.png)

Going into the /home folder we see there are 2 more directories, Morty and RickSanchez.

![image](https://user-images.githubusercontent.com/76552238/157480122-949fb799-5d64-440c-9977-66bca1171833.png)

The directory 'Morty' has a .jpg and a zip file.

![image](https://user-images.githubusercontent.com/76552238/157480541-efa5800d-20bf-4854-abd4-fee32cc2ea27.png)

We can use the 'strings' command to see if the jpg holds any secret information.

> Strings Safe_Password.jpg

![image](https://user-images.githubusercontent.com/76552238/157481400-6e75f9b7-4b62-43fc-8aa8-b7799d072154.png)

We can now unzip the zip file.

![image](https://user-images.githubusercontent.com/76552238/157481720-18df89ea-2d44-4645-9f39-17b9c8fe7d22.png)

Let's go to Rick's folder.

![image](https://user-images.githubusercontent.com/76552238/157482387-2ea3d60c-4a47-4f4c-b1b1-b19523afd291.png)

The directory 'ThisDoesntContainAnyFlags' suprisingly doesn't have any flag (FOR REAL).

![image](https://user-images.githubusercontent.com/76552238/157489833-038b2985-347b-44ff-99e2-893cc62763bb.png)

The second directory is RICKS_SAFE, it contains an exectuable named safe.

![image](https://user-images.githubusercontent.com/76552238/157482733-8ce9a526-525b-4627-8c15-f59ce2b55686.png)

We don't have permissions to execute the script, so let's download it to our local machine.

![image](https://user-images.githubusercontent.com/76552238/157483158-5c3bef0c-c24d-4736-8fd3-9d89f492a5ef.png)

Turns out we can pass arguments to the script.

![image](https://user-images.githubusercontent.com/76552238/157483673-7e869da1-31ce-4fcd-aeb9-c960d6b8ddb4.png)

In the last flag we found in Morty's directory there was a number. Let's see what happens when we pass it.

![image](https://user-images.githubusercontent.com/76552238/157483808-e23e3b34-2a36-4f05-95ad-cfc6e39c106a.png)

This message gives a clue into Rick's password. It holds holds 1 uppercase character, 1 number and a string from Rick's band name. Rick's band name is 
'The Flesh Curtains'. Let's write a simple python script that gives us all the possible combinations.

> python Ricks_Password.py > users.txt  

> hydra -l RickSanchez -P passCombinations.txt ssh://10.0.0.26:22222 -IV

![image](https://user-images.githubusercontent.com/76552238/157486812-bade2bb3-c5fd-48dc-b2aa-d0509136aacd.png)

Now that we are logged in the user 'RickSanchez' let's see if he is part of the sudo group.

![image](https://user-images.githubusercontent.com/76552238/157486441-9916f6ac-b832-4d08-af8a-5ba892a7911f.png)

![image](https://user-images.githubusercontent.com/76552238/157486650-deb32134-bb58-4dce-90d8-ec8b5bed23ec.png)

And with 130 points and 0 more to go the CTF is officaily completed.
