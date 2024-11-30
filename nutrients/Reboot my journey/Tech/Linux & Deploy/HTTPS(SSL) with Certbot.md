## Install free TLS/SSL certificates

1. Install Certbot
```
sudo apt install certbot python3-certbot-nginx
```

2. Confirming Nginx's Configuration by check server_name
```
sudo nano /etc/nginx/sites-available/example.com
```

3. Allow HTTPS through firewall
```
sudo ufw status
sudo ufw allow 'Nginx Full'
```

4. Obtaining an SSL Certificate
```
sudo certbot --nginx -d example.com -d www.example.com
```

## Enable HTTP2 supported

1. Modify Nginx Config site-enabled
```
sudo nano /etc/nginx/sites-available/default
```

- add https in listen 443 ssl line
```nginx
server {
    ...
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    
    server_name yourdomain.com;
    root /var/www/html;

    ssl_certificate /path/to/ssl/certificate.crt;
    ssl_certificate_key /path/to/ssl/private.key;

    # Ensure TLS protocols are correct
    ssl_protocols TLSv1.2 TLSv1.3;
}
```

3. Test nginx configuration
```bash
sudo nginx -t
```

4. Restart nginx
```bash
sudo systemctl restart nginx
```
