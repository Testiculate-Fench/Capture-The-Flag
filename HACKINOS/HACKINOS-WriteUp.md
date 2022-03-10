Source: https://www.vulnhub.com/entry/hackinos-1,295/  
Target: 10.0.0.29  
Difficulty: Medium

## NMAP 

> nmap -sS -A -T4 -p- 10.0.0.29

![image](https://user-images.githubusercontent.com/76552238/157764662-2bdff9d3-ccd0-4afa-8285-13c1761f867c.png)

Starting with a NMAP scan we see 2 open ports, SSH and HTTP, let's start by enumerating HTTP on port 8000 and try to get credentials to log to the machine with ssh.

## HTTP | Port 8000

From our NMAP scan we can see that port 8000 has a robots.txt file and is running WordPress.  

![image](https://user-images.githubusercontent.com/76552238/157765772-ae79b69a-d8fb-4aea-aa61-0f6f0c6859f6.png)

Going to 10.0.0.31/upload.php there is an option to upload an image. By using the dev tools we can find a little hint:

![image](https://user-images.githubusercontent.com/76552238/157765849-5e9213d0-b4b7-478e-89b7-d38f6e8de9c5.png)

<!-- https://github.com/fatihhcelik/Vulnerable-Machine---Hint -->

Following the link, we can see the source code for the upload.php page. The README.md file says the program has some security vulnerabilities.

**README.md** - 

    Don't use this code anywhere. Intentionally, they have got some security vulnerabilities.

    Hint for HackinOS vulnerable machine. Link: https://www.vulnhub.com/entry/hackinos-1,295/

**upload.php** - 
    <!DOCTYPE html>
    <html>

    <body>

    <div align="center">
    <form action="" method="post" enctype="multipart/form-data">
        <br>
        <b>Select image : </b> 
        <input type="file" name="file" id="file" style="border: solid;">
        <input type="submit" value="Submit" name="submit">
    </form>
    </div>
    <?php

    // Check if image file is a actual image or fake image
    if(isset($_POST["submit"])) {
        $rand_number = rand(1,100);
        $target_dir = "uploads/";
        $target_file = $target_dir . md5(basename($_FILES["file"]["name"].$rand_number));
        $file_name = $target_dir . basename($_FILES["file"]["name"]);
        $uploadOk = 1;
        $imageFileType = strtolower(pathinfo($file_name,PATHINFO_EXTENSION));
        $type = $_FILES["file"]["type"];
        $check = getimagesize($_FILES["file"]["tmp_name"]);

        if($check["mime"] == "image/png" || $check["mime"] == "image/gif"){
            $uploadOk = 1;
        }else{
            $uploadOk = 0;
            echo ":)";
        } 
    if($uploadOk == 1){
        move_uploaded_file($_FILES["file"]["tmp_name"], $target_file.".".$imageFileType);
        echo "File uploaded /uploads/?";
    }
    }
    ?>

    </body>
    </html>

The program checks if the image is not empty, if it is not empty, it hashes the name of the file and adds a random number to it.
The program checks if the MIME type of the image is either "image/png" or "image/gif" (MIME stands for "Multipurpose Internet Mail Extensions. It's a way of identifying files on the Internet according to their nature and format).

This means if we enter either a GIF or a PNG, the name of the file will be hashed and saved to the /uploads folder. The goal is to upload a PHP reverse shell and connect to the machine, we need to fool the program that our PHP code is an image or a gif.  
After playing with a few PNG files I found that the MIME type is stored in their metadata.

![image](https://user-images.githubusercontent.com/76552238/157766942-06df338a-f9e7-40ba-9207-a67b9c0dcd51.png)

 I searched for ways to change the MIME type but I did not succeed. I tried using Burp suite to capture the packet being uploaded and maybe change it a bit. I uploaded a png file and intercepted the packet, I saw the on the top of the source code was the string "PNG", I uploaded a gif image as well and there was the same thing only with "GIF89".
 
![image](https://user-images.githubusercontent.com/76552238/157767153-bd487f82-c29d-4b66-9972-dcfe9c1a37cd.png)

![image](https://user-images.githubusercontent.com/76552238/157767377-8a19cc4c-f90f-4746-aaca-e3ae5df8a7a2.png)

I tried uploading the reverse shell and adding "PNG" to it but it didn't work, but after adding "GIF89" it worked and the PHP script name was hashed and added to the /uploads directory.

![image](https://user-images.githubusercontent.com/76552238/157767505-026d5448-c688-4793-a130-b93a72374254.png)

![image](https://user-images.githubusercontent.com/76552238/157767565-d6c8b15f-4b35-4ba9-8b0b-90b3846665a8.png)

Now we need to find our uploaded PHP script and access it, since a random number from 1-100 is added in the end we'll make a python script that covers all options.

createHashesList.py - 

	import hashlib
	
	nameOfFile = "reverse_shell.php"
	for i in range(1,100):
	        hashedFileName = hashlib.md5((nameOfFile+str(i)).encode()).hexdigest()
        print(hashedFileName+".php")


> python3 createHashedList.py > list.txt

We can now use gobuster to see if our file is there.

> gobuster dir -u 10.0.0.29:8000/uploads -w list.txt

![image](https://user-images.githubusercontent.com/76552238/157768063-cf1e6d5a-1560-4bf0-a44d-853b571b7776.png)

![image](https://user-images.githubusercontent.com/76552238/157768142-a9548c76-5de3-4b1b-a1a6-6340638358c0.png)

>  nc -lnvp 4444

![image](https://user-images.githubusercontent.com/76552238/157768247-7f166264-ea07-4747-9180-e81fa5065478.png)

We now have access to the machine as the www-data user.
Reading the /etc/passwd file we find there is only the root user.

![image](https://user-images.githubusercontent.com/76552238/157768406-65481e88-c741-4cf0-8fbb-1ea85bc39b19.png)

 Let's try to find SUID files.

> find / -perm /4000 2> /dev/null

![image](https://user-images.githubusercontent.com/76552238/157768491-8fe41939-d438-4d6b-8386-88eed95e78cf.png)

We see that the tail command has SUID permissions. Since the tail command has SUID permissions we can read files with root only permission, such as the /etc/shadow file that holds hashed passwords for the machine users. 

> tail -n 20 /etc/shadow | grep root

![image](https://user-images.githubusercontent.com/76552238/157768609-4dd8082c-2e62-4a25-b8d3-1112d919bccf.png)

We can crack the hashed password using 'john' on our local machine.

> john rootHashedPassword.txt

![image](https://user-images.githubusercontent.com/76552238/157769021-8634bbe0-d4ed-4c1f-b19f-65c237a5e42a.png)

> su root

![image](https://user-images.githubusercontent.com/76552238/157769294-a84bb38d-a47d-45d3-9b74-bc706f5c301e.png)

By getting root and the flag we finished the CTF.
