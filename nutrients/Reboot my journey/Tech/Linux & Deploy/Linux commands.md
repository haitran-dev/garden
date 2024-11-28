### Files system

| Command               | Use                         | Example       | Output              |
| --------------------- | --------------------------- | ------------- | ------------------- |
| realpath ==filename== | Get full path of a file/dir | realpath .ssh | /Users/haitran/.ssh |

---
### User

| Command                            | Use                                               | Example                    | Output                               |
| ---------------------------------- | ------------------------------------------------- | -------------------------- | ------------------------------------ |
| adduser ==username==               | add user under /home                              | adduser prod               |                                      |
| ls /home                           | List user under /home                             |                            | ![[Pasted image 20241127113517.png]] |
| sudo usermod -aG sudo ==username== | Add user to sudo group<br>-a: append<br>-G: group | sudo usermod -aG sudo prod |                                      |
| su - ==username==                  | switch user                                       | su - prod                  |                                      |
|                                    |                                                   |                            |                                      |

---
### VPS Stats

| Command            | Use                                           | Example | Output                               |
| ------------------ | --------------------------------------------- | ------- | ------------------------------------ |
| free -h            | Show memory stats in human readable format    |         | ![[Pasted image 20241127142029.png]] |
| df -h              | Show free disk stats in human readable format |         | ![[Pasted image 20241127142624.png]] |
| htop (human - top) | View tasks manager in linux vps               |         | ![[Pasted image 20241127172058.png]] |
### Firewall

| Command                   | Use                                             | Example | Output                                   |
| ------------------------- | ----------------------------------------------- | ------- | ---------------------------------------- |
| ufw status                | View ubuntu firewall status                     |         | ![[Pasted image 20241127180639.png]]<br> |
| sudo ufw enable           | Enable ubuntu firewall                          |         | ![[Pasted image 20241127180656.png]]     |
| sudo systemctl enable ufw | Ensure firewall auto enable when system reboots |         | ![[Pasted image 20241127181114.png]]     |
| sudo ufw allow ssh        | Allo ssh on port 22                             |         | ![[Pasted image 20241127181638.png]]     |
|                           |                                                 |         |                                          |

> [!warning] Firewall issue
> 
> Need open port 22 (ssh) after enable firewall on vps for ssh from local machine


