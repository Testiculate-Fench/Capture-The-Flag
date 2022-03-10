Source: https://www.vulnhub.com/entry/derpnstink-1,221/  
Target: 10.0.0.28  
Difficulty: Medium

## NMAP 
> nmap -sS -T4 -p- 10.0.0.28

![image](https://user-images.githubusercontent.com/76552238/157495241-eaa4a132-9081-462f-8dfc-12a802d7504e.png)

There are 3 open ports on the machine, let's try to see if the FTP service allows anonymous login.
## FTP

> ftp 10.0.0.28

![image](https://user-images.githubusercontent.com/76552238/157495380-68ee42d4-ed5a-4cff-8188-1a9917db3f00.png)

Anonymous login is not allowed on this machine. We'll return to FTP later.

## HTTP

![image](https://user-images.githubusercontent.com/76552238/157495654-28ea7f1b-adb7-48ce-b564-ad92e3b1411d.png)

Going to http://10.0.0.28

Using the developer tools, we can find hidden in many div tags our first flag.

![image](https://user-images.githubusercontent.com/76552238/157495979-069c3cb7-e8d2-4feb-aaf5-9ac8516c799b.png)

Now let's brute force the directories using gobuster.

> gobuster dir -u http://10.0.0.28/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x txt,php

![image](https://user-images.githubusercontent.com/76552238/157496895-4a9067e3-6a62-4dca-8b8f-bd52402e2aca.png)

> http://10.0.0.26/temporary

![image](https://user-images.githubusercontent.com/76552238/157498420-ae193899-da04-4acd-a9b4-75c42ef30c70.png)

I'm trying :').  It doesn't have any comments or hidden files.
But the 'php' directory is a different story, at first it tells us we don't have permission to access it, but if we brute force its directories we find it runs the service PhpMyAdmin.  
(PhpMyAdmin is a free software tool written in PHP, intended to handle the administration of MySQL over the Web)

> gobuster dir -u http://10.0.0.28/php/ -w /usr/share/wordlists/dirb/common.txt

![image](https://user-images.githubusercontent.com/76552238/157499082-8dd93d73-ed9f-4c61-951a-11506a50eba8.png)

![image](https://user-images.githubusercontent.com/76552238/157499795-92355261-470e-4740-8e1e-52290d80af71.png)

We will return when we find credentials.

Going to the /weblog directory I was redirected to http://derpnstink.local/weblog/.

![image](https://user-images.githubusercontent.com/76552238/157500007-6eae541c-7387-41c4-9397-05d4421cff6e.png)

This means the domain name of the webserver is "derpstink.local". Let's add it to the hosts file.  

> gobuster dir -u http://derpnstink.local/weblog/ -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt

![image](https://user-images.githubusercontent.com/76552238/157679798-c1945390-05e5-4107-9998-be7597f74b81.png)

From the results we can see that this site is running on Wordpress.  
Using "wpscan" we can find usernames to try and brute force the login. 

> wpscan -e u,p,t -v --url http://derpnstink.local/weblog/

We found one user. 

![image](https://user-images.githubusercontent.com/76552238/157680244-115a2f44-fbec-4596-b701-c5fabd973c57.png)

And also one plugin.

![image](https://user-images.githubusercontent.com/76552238/157680789-3c2311e5-a4af-48d8-949f-cdb1ec0516d7.png)

Let's brute force the login using the username 'admin'.

> wpscan -U 'admin' -P /usr/share/wordlists/rockyou.txt --url http://derpnstink.local/weblog/

Logging into the admin panel we can only see the access the slideshows plugin we found in our scan. Usually what I do is upload a reverse shell as a plugin, or change the PHP code of a page to a reverse shell script but here we don't have that.  
I searched for 'Wordpress slideshow cve' but I couldn't find any ones with high ratings, so I went to Metasploit and searched for 'Wordpress slideshow' and found an exploit.

![image](https://user-images.githubusercontent.com/76552238/157682480-876c6ae8-041b-4167-a682-d7896196460f.png)

After running the exploit we are able to get a reverse shell on the machine.

![image](https://user-images.githubusercontent.com/76552238/157682788-4dfdea15-97a2-47b2-934a-6a5ca6ce61af.png)

Going to the /home folder we can see 2 users. We don't have permission to their directories so we will have to come back to them later.

![image](https://user-images.githubusercontent.com/76552238/157686028-e8c975f6-0c67-46cf-9b40-29d3fda83626.png)

Going to /var/www/html/weblog we find the wp-config.php file. It stores the password for the root user.

![image](https://user-images.githubusercontent.com/76552238/157683044-ec54109c-02ff-4716-8e13-87fafaecfa80.png)

I tried to login to with the password to the machine with ssh but it doesn't accept passwords, only keys, so I remembered 'Phpmyadmin' was running on the webserver so I tried login and got access.

![image](https://user-images.githubusercontent.com/76552238/157683281-108380aa-4a22-4ca9-ab2b-8b96a1fed29f.png)

In the weblog database, that 'wp_users' table held this credentials.

![image](https://user-images.githubusercontent.com/76552238/157685463-7b584a91-7d3e-476d-98b6-15b961bb3acd.png)

We already know that password for the user 'admin' is 'admin'. Their passwords are hashed, but we can use 'john' or CrackStation to crack them.

![image](https://user-images.githubusercontent.com/76552238/157685762-a3d54f25-420c-4c8c-aafd-0c3bcca719a9.png)

> unclestinky:wedgie57

Going back to our reverse shell, we now have the password for the user stinky. We can't SSH to the user, it requires a key.  

> ssh stinky@10.0.0.28

![image](https://user-images.githubusercontent.com/76552238/157686960-d4095406-1086-4527-93c4-0852397b452f.png)

But we can log in via the machine.

![image](https://user-images.githubusercontent.com/76552238/157686656-7059965e-d535-48a8-b7be-66acbde42186.png)

Going to /home/stinky/Desktop, we can find the third flag.

![image](https://user-images.githubusercontent.com/76552238/157687148-4e8978b2-654b-4dcd-80d9-1bacd57b1dc8.png)

## 'FTP' AS STINKY

We don't really have to log in to FTP, because FTP's directories are stored on the home folder of the user.

![image](https://user-images.githubusercontent.com/76552238/157687934-618be54d-9a79-4343-9526-714d99e9d45f.png)

The directory '/home/stinky/ftp/files' holds some interesting information.

![image](https://user-images.githubusercontent.com/76552238/157688362-ec5ce118-fff5-445d-8354-ba3f0d8e485b.png)

Going to the 'ssh' directory there 6 more nested 'ssh' directories. After getting to the final one we get a public key. 

![image](https://user-images.githubusercontent.com/76552238/157688852-700878c0-bc7f-42f2-910c-f7b5d0baca14.png)

I tried logging in to the root user on the machine but it wasn't the right key, turns out the key is for the stinky user, but we are already logged in so this step was unnecessary.

But the directory 'network-log' is actually helpful.

![image](https://user-images.githubusercontent.com/76552238/157689560-8584ad2d-6c1d-4957-874e-91c23ee05ba5.png)

This means there is a file we need to open with Wireshark and find the password for the user 'mrderp'.

Going to the /home/stinky/Documents directory, we can find the .pcap file.

![image](https://user-images.githubusercontent.com/76552238/157690066-a4e4de3c-144f-4eb0-9a40-d995d2551d03.png)

After opening it with Wireshark, we can filter the packets to HTTP.

![image](https://user-images.githubusercontent.com/76552238/157692047-6265fc08-0e4e-4d31-a221-f5ef23d4cf05.png)

Following the packets sent, I found the packet that 'mrderp' sent to the server to log in and got the password.

![image](https://user-images.githubusercontent.com/76552238/157691843-d33787e5-3667-420d-88cd-c321ede6ce3a.png)

> mrderp:derpderpderpderpderpderpderp

![image](https://user-images.githubusercontent.com/76552238/157692306-a1de4677-1601-48d8-a993-8caad5b98cd2.png)

We are now logged in as the user 'mrderp'.  

## PRIVILEGE ESCALATION

/home/mrderp/ doesn't have any files or information.

![image](https://user-images.githubusercontent.com/76552238/157693169-4c515898-7634-47a1-b226-6045914c83dc.png)

Let's see if the user has any root permissions.

![image](https://user-images.githubusercontent.com/76552238/157692731-6f2e2559-fd6d-4152-86a4-2458dc00cdef.png)

As we saw earlier there is no directory called 'binaries'. Let's try to create a file with the name and path specified and see if we can get a shell as root.

![image](https://user-images.githubusercontent.com/76552238/157693843-ee367e27-8c41-49ef-aec4-3dffb7a316fe.png)

![image](https://user-images.githubusercontent.com/76552238/157694475-7a505022-8884-45b1-ba56-07ec76d9962b.png)

Now that we are logged in as the root user we can read the final flag.

![image](https://user-images.githubusercontent.com/76552238/157694673-cc752fbb-b9d8-4a82-9b37-83846a6cd392.png)
