![image](https://user-images.githubusercontent.com/76552238/157273188-295c617c-4543-4ec6-a843-24fe442d243a.png)

>- Source: https://www.vulnhub.com/entry/the-planets-mercury,544/  
>- Difficulty: Easy  
>- Target IP: 10.0.0.26  

### NMAP
![image](https://user-images.githubusercontent.com/76552238/157274108-605c7da0-e5f8-48e4-946b-ed2f48807fdb.png) 

Starting with an NMAP scan, we have 2 open services on the machine, SSH on 22 and an HTTP proxy on 8080. 

### HTTP
Going to http://10.0.0.26, it stats the site is still in devlopment.
![image](https://user-images.githubusercontent.com/76552238/157290319-4ca376c3-2c3c-4fbf-9440-e5be921b79a6.png)  
There are no comments or cookies on the web server. Let's try to brute force the directories.

![image](https://user-images.githubusercontent.com/76552238/157291097-d5eb4839-65c1-4a58-aeaa-1c3590f31431.png)

'robots.txt' doesn't hold useful information for us. I accidently typed 'robot.txt' and turns out the 404 error page gives us information on a secret directory. :o

![image](https://user-images.githubusercontent.com/76552238/157292211-dfb3afe4-da2a-4aac-93d3-34ac6e741e5e.png)

Going to http://10.0.0.26:8080/mercuryfacts/ we have 2 hyperlinks.

![image](https://user-images.githubusercontent.com/76552238/157293280-1891ae6d-d8ca-434a-9b15-9fe41c41bfd4.png)

mercuryfacts/todo:

![image](https://user-images.githubusercontent.com/76552238/157293591-4fcc86b5-301d-4c5e-9df4-d7c228912803.png)

By the todo list the author left, we can assume this site in vulnerable to SQLi, but where? ;)

/mercuryfacts/1/:

![image](https://user-images.githubusercontent.com/76552238/157294366-43c5c3c7-c9a7-4c8d-a827-575b46d0d277.png)

I tried playing around with the fact number in the url, there are in total 8 facts (1-8) and when we enter a different number there is no error and no output.

![image](https://user-images.githubusercontent.com/76552238/157294914-5ce726dc-a3d3-4c9f-9e10-025409cdd2cb.png)

We can assume this pulls data from a database and where our SQLi will be (and also becuase there are no other files or directories). 
When we enter a quetation mark (') we get this error.

![image](https://user-images.githubusercontent.com/76552238/157296221-57f6f3ad-d5c2-4554-9199-4a3450a30e96.png)

Let's use 'sqlmap'.

> sqlmap -u http://10.0.0.26:8080/mercuryfacts/ --dbs --batch

![image](https://user-images.githubusercontent.com/76552238/157298155-69788bca-5dd8-4b7a-a32a-b056f5476c41.png)

'information_schema' holds information about the sql server so it won't be helpful for us, but the database 'mercury' seems intersting.

> sqlmap -u http://10.0.0.26:8080/mercuryfacts/ -D mercury --tables --batch

![image](https://user-images.githubusercontent.com/76552238/157299374-3b6fdb0d-bac6-4ba1-ba60-6d1473e689c7.png)

> sqlmap -u http://10.0.0.26:8080/mercuryfacts/ -D mercury -T users --columns --batch --dump

![image](https://user-images.githubusercontent.com/76552238/157299572-146c2f1f-16cc-412d-8e28-f3f82fa9ecd4.png)

By adding the usernames and passwords we found into seperate files we can use hydra and brute force the SSH login.

> hydra -L users.txt -P passwords.txt ssh://10.0.0.26 -IV

![image](https://user-images.githubusercontent.com/76552238/157300152-415f1fc5-1843-40a3-85b5-6947e04de04f.png)

