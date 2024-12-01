## What is this ?
- SSH = Secure shell
- is cryptographic network protocol used to securely access using public-private key pair
- used for secure remote login

## VPS IP

```
143.198.194.97
```

## Commands

| Command                            | Use                   | Example                 |
| :--------------------------------- | :-------------------- | ----------------------- |
| ssh-keygen                         | Create ssh key        |                         |
| ssh -T ==user==@==hostname_or_ip== | Verify ssh connection | ssh -T git@github.com   |
| ssh ==user==@==hostname_or_ip==    | SSH to remote vps     | ssh root@143.198.194.97 |
|                                    |                       |                         |
## Alias ssh with custom ssh key

- Option 1 - Use custom ssh command

```
ssh -i /Users/haitran/.ssh/id_ed25519_digital_ocean -v root@143.198.194.97
```

- Option 2 - Add alias in .ssh/config and use alias

```
Host ubuntu-all-in-one
HostName 143.198.194.97
User root
IdentityFile /Users/haitran/.ssh/id_ed25519_digital_ocean
IdentitiesOnly yes
Port 22
```

```
ssh ubuntu-all-in-one
```
