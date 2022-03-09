Source: https://www.vulnhub.com/entry/derpnstink-1,221/  
Target: 10.0.0.28  
Difficulty: Medium

## NMAP 
> nmap -sS -T4 -p- 10.0.0.28

![image](https://user-images.githubusercontent.com/76552238/157495241-eaa4a132-9081-462f-8dfc-12a802d7504e.png)

There are 3 open ports on the machine, let's try to see if the FTP service allowes anonymous login.
## FTP

> ftp 10.0.0.28

![image](https://user-images.githubusercontent.com/76552238/157495380-68ee42d4-ed5a-4cff-8188-1a9917db3f00.png)

Anoynmous login is not allowed on this machine. We'll return to FTP later.

## HTTP

![image](https://user-images.githubusercontent.com/76552238/157495654-28ea7f1b-adb7-48ce-b564-ad92e3b1411d.png)

Going to http://10.0.0.28

Using the developer tools, we can find hidden in many div tags our first flag .

![image](https://user-images.githubusercontent.com/76552238/157495979-069c3cb7-e8d2-4feb-aaf5-9ac8516c799b.png)

Now let's brute force the directories using gobuster.

> gobuster dir -u http://10.0.0.28/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x txt,php

![image](https://user-images.githubusercontent.com/76552238/157496895-4a9067e3-6a62-4dca-8b8f-bd52402e2aca.png)

> http://10.0.0.26/temporary

![image](https://user-images.githubusercontent.com/76552238/157498420-ae193899-da04-4acd-a9b4-75c42ef30c70.png)

I'm trying :').  It doesn't have any comments or hidden files.
But the php directory is a different story, at first it tells us we don't have permission to access the directory, if we brute force its directories we find it runs phpmyadmin.

> gobuster dir -u http://10.0.0.28/php/ -w /usr/share/wordlists/dirb/common.txt

![image](https://user-images.githubusercontent.com/76552238/157499082-8dd93d73-ed9f-4c61-951a-11506a50eba8.png)

![image](https://user-images.githubusercontent.com/76552238/157499795-92355261-470e-4740-8e1e-52290d80af71.png)

We will return when we find credentials.

Going to the /weblog directory I was redirected to http://derpnstink.local/weblog/.

![image](https://user-images.githubusercontent.com/76552238/157500007-6eae541c-7387-41c4-9397-05d4421cff6e.png)

This means the domain name of the webserver is "derpstink.local". Let's add it to the hosts file.
Brute forcing the directories on http://derpstink/weblog we find out it runs Wordpress.
Using "wpscan" we can find usernames to try and bruteforce the login, we find a username ---> admin.

root@kali ~/D/C/DERPNSTINK [4]# wpscan -U 'admin' -P /usr/share/wordlists/rockyou.txt --url http://derpnstink.local/weblog/

We found the password for the admin user.

Username: admin, Password: admin

Loggin in to the admin panel we can only see the access the Slideshows, now usually what I do is upload a revese shell plugin or change the php code of a page to a reverse shell script but here we don't have that.
I searched for Wordpress slideshow cve but I couldn't find any ones with high ratings, so I went to metasploit and searched for Wordpress slideshow and found an exploit.

unix/webapp/wp_slideshowgallery_upload

After setting the needed changes to options I checked to see if the the target is vulnerable, and we have approvel, running the exploit we get a meterpreter session.
We can enter the shell command to get shell access the the machine.

whoami
www-data

We can use python to get a better shell ---> python3 -c 'import pty; pty.spawn("/bin/bash")'

Going to /var/www/html/weblog we find the wp-config.php file. It stores the password for the root user.

/** MySQL database username */
define('DB_USER', 'root');

/** MySQL database password */
define('DB_PASSWORD', 'mysql');

I tried to login to with the password to the machine with ssh but it doesn't accept passwords, only keys, so I remembered phpmyadmin was running the webserver so I tried login and got access. Now that we have access we can see the users and even change passwords.
After some diggin I found the second flag in one of the tables.

flag2(a7d355b26bda6bf1196ccffead0b2cf2b81f0a9de5b4876b44407f1dc07e51e6)

Going to the wp-users table in the wordpress database we see 2 users:
admin
unclestinky

We can also see their hashed passwords, we can try using john the ripper to help us crack the hash.

root@kali ~/D/C/DERPNSTINK# john -w=/usr/share/wordlists/rockyou.txt uncleystinky_hash.txt 

Cracked password ---> wedgie57

Trying to log in via Wordpress we have access.
I tried uploading a reverse shell but it didn't work so I went back the revese shell we had with the user www-data and found out there there is the user stinky on the machine, I tried to log with the same password we found for Wordpress and we have access.
Going to the /home/stinky/Desktop directory we can find the third flag.

flag3(07f62b021771d3cf67e2e1faf18769cc5e5c119ad7d4d1847a11e11d6d5a7ecb)
---------------------------------------------------------------------------------------------------------
FTP AS STINKY
---------------------------------------------------------------------------------------------------------
Now that we have a username let's see if we can log in to ftp. The same credintials also work on ftp, wow this guy is a not a very good sysadmin.
After entering the "files" directory we see a direcory named network-logs, it holds a converstion between two user.

derpissues.txt:
12:06 mrderp: hey i cant login to wordpress anymore. Can you look into it?
12:07 stinky: yeah. did you need a password reset?
12:07 mrderp: I think i accidently deleted my account
12:07 mrderp: i just need to logon once to make a change
12:07 stinky: im gonna packet capture so we can figure out whats going on
12:07 mrderp: that seems a bit overkill, but wtv
12:08 stinky: commence the sniffer!!!!
12:08 mrderp: -_-
12:10 stinky: fine derp, i think i fixed it for you though. cany you try to login?
12:11 mrderp: awesome it works!
12:12 stinky: we really are the best sysadmins #team
12:13 mrderp: i guess we are...
12:15 mrderp: alright I made the changes, feel free to decomission my account
12:20 stinky: done! yay

This means there is a file we need to open with wireshark and find the password for mrderp.

Going back to the files direcotry there is a directory named ssh, after logging in it holds another directory called ssh and then another and so on...
After 7 direcoties we get to the key.
This means we can log in via ssh. I tried logging in to the root user but it wasn't the right key, turns out the key is for the stinky user, but we are already logged in so this step was unnecessary.

---------------------------------------------------------------------------------------------------------
PRIVILEGE ESCALATION
---------------------------------------------------------------------------------------------------------
stinky@DeRPnStiNK:~/ftp/files$ sudo -l
[sudo] password for stinky: wedgie57

Sorry, user stinky may not run sudo on DeRPnStiNK.

We don't have root permissions as stinky.
Reading the /etc/passwd file we see there are 2 nonroot users:
stinky
mrderp

We are logged in as the stinky user so our goal is to either get root or the mrderp user who should have higher privelages then our current user has.
On the home folder there is a folder called ftp, since we already enuemrated ftp it doesn't have any use to us.
Going to the documents folder we find a .pcap file as stated by the converstion we found in the ftp server.

Opening it and filtering the packets to http.request.method==POST, because we want to find the packet where the new user was created, because this HTTP we can via the password. 

Afer finding the packet we see the password for mrderp is ---> "derpderpderpderpderpderpderp"

We can now log in to as mrderp.

mrderp@DeRPnStiNK:~/Desktop$ sudo -l

Matching Defaults entries for mrderp on DeRPnStiNK:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User mrderp may run the following commands on DeRPnStiNK:
    (ALL) /home/mrderp/binaries/derpy*

The mrderpy user can run the command specicifed as root. Trying to run it we are informed that the path does not exist, if we try to create the direcotry and file and run them as root we can add whatever command we want to the file and run it as root.

mrderp@DeRPnStiNK:~$ mkdir binaries;cd binaries
mrderp@DeRPnStiNK:~/bianries$ touch derpy
mrderp@DeRPnStiNK:~/binaries$ chmod +x derpy 
mrderp@DeRPnStiNK:~/binaries$ sudo ./derpy

We don't get any errors, this means we can edit the file to open a new bash shell.
Running the file with sudo we get a shell as the root user, we can now read the final flag.

flag4(49dca65f362fee401292ed7ada96f96295eab1e589c52e4e66bf4aedda715fdd)

Congrats on rooting my first VulnOS!

Hit me up on twitter and let me know your thoughts!

@securekomodo


root
