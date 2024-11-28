Config Nginx for VPS

1. Install NGINX
```bash
sudo apt update
sudo apt install nginx
```

2. Open firewall for nginx (80 for HTTP and 443 for HTTPS)
```bash
sudo ufw allow 'Nginx Full'
```

3. Verify nginx is running
```bash
systemctl status nginx
```

4. Create site config
```bash
sudo nano /etc/nginx/sites-available/site_name.conf
```

5. Add configuration
```nginx
server {
    listen 80;
    server_name frontcent.com www.frontcent.com;

    # Proxy requests to the application on port 8080
    location / {
        proxy_pass http://127.0.0.1:8080;  # Change to your app's internal IP if not on the same machine
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Optional: Error page if something goes wrong
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
```

6. Enable configuration
```bash
sudo ln -s /etc/nginx/sites-available/site_name.conf /etc/nginx/sites-enabled/
```

7. Test NGINX config
```bash
sudo nginx -t
```

8. Reload NGINX`
```bash
sudo systemctl restart nginx
```
