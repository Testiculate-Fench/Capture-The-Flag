<!--Don't know if to keep the last paragraph because I was not able to find the final flag on the second machine-->

**Target: 10.0.0.37**  
**Difficulty: Medium**  
**Source: *https://www.vulnhub.com/entry/super-mario-host-101,186/***

## ***NMAP***

    $ nmap -sS -T4 -p- 10.0.0.37

    PORT     STATE SERVICE
    22/tcp   open  ssh                                                                                        
    8180/tcp open  unknown 

## ***PORT 8180***

![image](https://user-images.githubusercontent.com/76552238/159245535-1707036c-d491-466a-a956-afc8f6ff8e97.png)

Going to ***http://10.0.0.37:8180*** there is nothing interesting or useful, let's try to brute force the directories.

    $ gobuster dir -u http://10.0.0.37:8180/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt

    /vhosts               (Status: 200) [Size: 1364]
    /server-status        (Status: 403) [Size: 215] 

### ***http://10.0.0.37:8180/vhosts:***

![image](https://user-images.githubusercontent.com/76552238/159245809-fe5492a5-7118-454a-af7c-7f56f2bbddbd.png)

<!-- ServerName mario.supermariohost.local
ServerAdmin webmaster@localhost
DocumentRoot /var/www/supermariohost
DirectoryIndex mario.php -->

The file stats that the Server name is 'mario.supermariohost.local', we can add it to our ***/etc/hosts*** file.

echo '10.0.0.37 mario.supermariohost.local' >> /etc/hosts

We can now go to ***mario.supermariohost.local:8180***. 

![image](https://user-images.githubusercontent.com/76552238/159246342-76fe3e86-2f0b-4d99-8c3a-d54a039692fb.png)

This time the site has some functionality but nothing interesting again.
Let's try to find hidden files.

    $ gobuster dir -u http://mario.supermariohost.local:8180/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,txt,html

/mario.php            (Status: 200) [Size: 7080]
/command.php          (Status: 200) [Size: 231]
/luigi.php            (Status: 200) [Size: 386]

![image](https://user-images.githubusercontent.com/76552238/159246686-0febada6-dfbb-4d6a-a228-09133cff5787.png)

Going to command.php, it says it finds users but all it does is spout out random output, so nothing interesting here.

Going to ***mario.supermariohost.local:8180/luigi.php*** it seems like Luigi left his brother a message.

![image](https://user-images.githubusercontent.com/76552238/159246824-a1b44d1e-00e6-40f3-b097-da5237fc24bb.png)

<!--Hey!! It'sa Luiiiggiii!!
My short brother doesn't know that I'm wandering around his host and messing around, he's new with computers!
Since I'm here I want to tell you more about myself...my brother is a nice person but we are in love for the same person: Princess Peach! I hope she will find out about this.
I Love Peach
Forever yours,
Luigi-->

This means we know about 3 possible users:

    mario
    luigi
    peach

Let's try to brute force SSH with those users.

    $ for user in mario luigi peach; do echo $user >> usernames.txt; done
    $ hydra -L usernames.txt -P /usr/share/wordlists/rockyou.txt ssh://10.0.0.37 -IV

luigi:luigi1

## ***SSH***

![image](https://user-images.githubusercontent.com/76552238/159247826-51949ce5-4702-4440-9126-2f21f2e6f0b3.png)

Logging in to the machine via SSH we are spawned with a restricted shell.

![image](https://user-images.githubusercontent.com/76552238/159247996-d7fb7065-d4bf-4cc9-9420-06b6364a5e24.png)


It seems like Mario has left Luigi a message.  

### ***message:***

    YOU BROTHER! YOU!! 
    I had to see it coming!!
    Not only you declare your love for Pricess Peach, my only love and reason of life (and lives, depending from the player), but you also mess with my server!
    So here you go, in a limited shell! Now you can't do much, MUHAUHAUHAUHAA

    Mario.

Using '?' we can see what commands we are allowed to run. 

    $ ?
    awk  cat  cd  clear  echo  exit  help  history  ll  lpath  ls  lsudo  vim

'awk' is one of them.
Searching for awk privilege escalation, I found a post from GTFbins ***https://gtfobins.github.io/gtfobins/awk/***

![image](https://user-images.githubusercontent.com/76552238/159248444-a0f11090-473c-40e3-a9ef-c8d613b8cd76.png)

After playing around with machine I found that the kernel version is vulnerable to an exploit ---> ***https://www.exploit-db.com/exploits/37292***

    $ uname -a
    Linux supermariohost 3.13.0-32-generic #57-Ubuntu SMP Tue Jul 15 03:51:08 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux

![image](https://user-images.githubusercontent.com/76552238/159248977-44ac26d7-6a73-4d75-b15d-5568b5281bbb.png)

After downloading and executing the exploit on the victim machine, we are able to a root shell.

Going to /root we find a zip file that is holding the flag. 

![image](https://user-images.githubusercontent.com/76552238/159249137-70b6e298-36d9-491d-8184-989e6ff9581e.png)

But it requires a password. I downloaded it to my local machine and by using 'zip2john' I was able to find the password for the zip file.

![image](https://user-images.githubusercontent.com/76552238/159249408-cc0f8073-89d9-42b8-b553-042f38ac9a98.png)

<!-- password for zip file: ilovepeach -->

![image](https://user-images.githubusercontent.com/76552238/159249564-8e80e658-7990-4320-819c-370d8e3b7e7e.png)

Let's try to get all the passwords: 'mario' 'root'

    root:$6$ZmdseK46$FTvRqEZXdr3DCX2Vd6CXWmWAOJYIjcAI6XQathO3/wgvHEoyeP6DwL3NHZy903HXQ/F2uXiTXrhETX19/txbA1:17248:0:99999:7:::

    mario:$6$WG.vWiw8$OhoMhuAHSqPYTu1wCEWNc4xoUyX6U/TrLlK.xyhRKZB3SyCtxMDSoQ6vioNvpNOu78kQVTbwTcHPQMIDM2CSJ.:17248:0:99999:7:::

Turns out there was another machine that was downloaded on the network where we are able to connect via SSH and get the final flag, but unfortunately because I'm running the machine no a bridged connection I was not able to get.
