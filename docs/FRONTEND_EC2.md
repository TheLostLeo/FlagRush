# Lightweight Frontend on Separate EC2 (Free Tier)

This is a static HTML/CSS/JS frontend that talks to the FlagRush backend APIs. It requires no Node.js runtime in production and can be served by Nginx.

## Files

- `frontend/index.html` — UI shell
- `frontend/styles.css` — basic styling
- `frontend/app.js` — minimal logic (login/register, list challenges, submit flags, leaderboard, stats)
- `frontend/config.example.js` — copy to `config.js` and edit MAIN_API_URL to your backend URL

## 1) Launch a small EC2 for frontend

- AMI: Amazon Linux 2023 (or Ubuntu 22.04)
- Instance type: t2.micro/t3.micro (Free Tier)
- Security Group inbound: HTTP 80 (from internet), SSH 22 (from your IP)

## 2) Install Nginx and deploy static files

```bash
sudo dnf update -y
sudo dnf install -y nginx

# Deploy files
sudo mkdir -p /var/www/flagrush
cd /var/www/flagrush
# Copy your local frontend folder here (use scp) or pull from git
# Example with scp:
# scp -r frontend/ ec2-user@<frontend-ec2-ip>:/var/www/flagrush/

# Create config.js with your backend URL
sudo bash -c 'cat > /var/www/flagrush/config.js' <<'EOF'
window.CONFIG = {
  MAIN_API_URL: 'http://<backend-ec2-ip>:5000'
};
EOF

# Nginx site config (simple)
sudo bash -c 'cat > /etc/nginx/conf.d/flagrush.conf' <<'EOF'
server {
  listen 80 default_server;
  server_name _;
  root /var/www/flagrush;
  index index.html;

  location / {
    try_files $uri $uri/ =404;
  }
}
EOF

sudo systemctl enable nginx
sudo systemctl restart nginx
```

Visit: `http://<frontend-ec2-ip>/`.

## 3) Backend CORS

Set the backend `CORS_ALLOW_ORIGINS` to your frontend origin (e.g., `http://<frontend-ec2-ip>`). Example in `/etc/sysconfig/flagrush.env`:

```bash
CORS_ALLOW_ORIGINS=http://<frontend-ec2-ip>
```

Reload backend services after changes.

## 4) Health check

- Frontend header shows backend health (`/health`).
- Login/Register users; token is stored in localStorage.
- Challenges list, details, flag submission, leaderboard, and stats use the backend APIs.

## Notes

- To enable HTTPS for frontend, install Certbot and configure TLS on Nginx.
- Restrict backend port 5000 to only allow inbound from the frontend EC2’s security group for extra safety, or proxy backend via Nginx HTTPS.
