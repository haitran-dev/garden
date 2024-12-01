### CI/CD with github actions free

1. Create workflows folder in repository
	![[Pasted image 20241201173136.png]]

2. Fill content in deployment files   
```yml
name: Deploy to prod user on VPS

on:
    push:
        branches: ["main"]

permissions:
    contents: read

jobs:
    build:
        runs-on: ubuntu-24.04
        steps:
            - name: Checkout repository
              uses: actions/checkout@v4

            - name: Setup Node.js
              uses: actions/setup-node@v4
              with:
                  node-version: 20

            - name: Create .env file
              run: echo "${{secrets.ENV_PROD}}" > .env

            - name: Install dependencies
              run: npm install

            - name: Build
              run: npm run build
    deploy:
        needs: build
        runs-on: ubuntu-24.04
        steps:
            - name: Deploy on VPS via SSH
              uses: appleboy/ssh-action@v0.1.6
              with:
                  host: ${{ secrets.HOST_PROD }}
                  username: ${{ secrets.USER_PROD }}
                  key: ${{ secrets.KEY_PROD }}
                  passphrase: ${{ secrets.SSH_PASSPHRASE_PROD }}
                  port: ${{ secrets.PORT_PROD }}
                  script: |
                      export NVM_DIR=~/.nvm
                      source ~/.nvm/nvm.sh
                      cd ~/portfolio
                      git fetch --all
                      git reset --hard origin/main
                      git pull origin main
                      echo "${{secrets.ENV_PROD}}" > .env
                      npm i --force
                      npm run build
                      pm2 restart portfolio-preview

```

3. Enter secret keys on repo setting
![[Pasted image 20241201190636.png]]