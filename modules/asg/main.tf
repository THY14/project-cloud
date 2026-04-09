# Get latest Amazon Linux 2 AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# Launch Template
resource "aws_launch_template" "main" {
  name_prefix   = "${var.project_name}-lt-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type

  iam_instance_profile {
    name = var.iam_instance_profile
  }

  network_interfaces {
    associate_public_ip_address = true
    security_groups             = [var.security_group_id]
  }

  user_data = base64encode(<<-EOF
    #!/bin/bash
    set -e
    exec > /var/log/userdata.log 2>&1

    # ── 1. System update ──────────────────────────────────────
    yum update -y
    yum install -y git python3 python3-pip nginx

    # ── 2. Install Node.js 18 ─────────────────────────────────
    curl -fsSL https://rpm.nodesource.com/setup_18.x | bash -
    yum install -y nodejs

    # ── 3. Clone GitHub repo ──────────────────────────────────
    git clone https://github.com/THY14/project-cloud.git /app
    cd /app/app

    # ── 4. Install Python dependencies ────────────────────────
    pip3 install fastapi uvicorn pandas numpy scipy requests scikit-learn python-multipart

    # ── 5. Run ML pipeline to generate model files ────────────
    python3 main.py

    # ── 6. Build Vue frontend 
    cd /app/app/frontend
    npm install
    npm run build
    cp -r dist/* /usr/share/nginx/html/

    # ── 7. Configure Nginx ────────────────────────────────────
    # Serves Vue on / and proxies /api/ to FastAPI on port 8000
    cat > /etc/nginx/conf.d/app.conf <<'NGINX'
    server {
        listen 80;

        location /api/ {
            proxy_pass http://127.0.0.1:8000/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
        }
    }
    NGINX

    systemctl enable nginx
    systemctl start nginx

    # ── 8. Run FastAPI as a systemd service
    cat > /etc/systemd/system/fastapi.service <<'SERVICE'
    [Unit]
    Description=FastAPI CADTFLIX Movie Recommendation
    After=network.target

    [Service]
    WorkingDirectory=/app/app
    ExecStart=/usr/bin/python3 -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
    Restart=always
    RestartSec=5

    [Install]
    WantedBy=multi-user.target
    SERVICE

    systemctl daemon-reload
    systemctl enable fastapi
    systemctl start fastapi
  EOF
  )

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "${var.project_name}-ec2"
    }
  }
}

# Auto Scaling Group
resource "aws_autoscaling_group" "main" {
  name                      = "${var.project_name}-asg"
  desired_capacity          = 2
  min_size                  = 1
  max_size                  = 4
  vpc_zone_identifier       = var.public_subnet_ids
  target_group_arns         = [var.target_group_arn]
  health_check_type         = "ELB"
  health_check_grace_period = 600

  launch_template {
    id      = aws_launch_template.main.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "${var.project_name}-asg-instance"
    propagate_at_launch = true
  }
}

# Scale Up Policy (CPU > 70%)
resource "aws_autoscaling_policy" "scale_up" {
  name                   = "${var.project_name}-scale-up"
  scaling_adjustment     = 1
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.main.name
}

# Scale Down Policy (CPU < 30%)
resource "aws_autoscaling_policy" "scale_down" {
  name                   = "${var.project_name}-scale-down"
  scaling_adjustment     = -1
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.main.name
}
