provider "aws" {
  region = "ap-southeast-1"
}

# =====================
# VPC
# =====================
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "terraform-vpc"
  }
}

# =====================
# PUBLIC SUBNET
# =====================
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true

  tags = {
    Name = "terraform-public-subnet"
  }
}

# =====================
# PRIVATE SUBNET
# =====================
resource "aws_subnet" "private" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.2.0/24"

  tags = {
    Name = "terraform-private-subnet"
  }
}

# =====================
# INTERNET GATEWAY
# =====================
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "terraform-igw"
  }
}

# =====================
# ROUTE TABLE (PUBLIC)
# =====================
resource "aws_route_table" "rt" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "terraform-rt"
  }
}

# Route ke internet
resource "aws_route" "route" {
  route_table_id         = aws_route_table.rt.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.gw.id
}

# Hubungkan route ke PUBLIC subnet saja
resource "aws_route_table_association" "assoc" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.rt.id
}

# =====================
# SECURITY GROUP
# =====================
resource "aws_security_group" "sg" {
  name   = "allow-ssh-http"
  vpc_id = aws_vpc.main.id

  # SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTP
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Outbound
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "terraform-sg"
  }
}

# =====================
# EC2 PUBLIC SERVER
# =====================
resource "aws_instance" "public" {
  ami           = "ami-0df7a207adb9748c7"
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.public.id
  key_name      = "my-key"

  associate_public_ip_address = true

  vpc_security_group_ids = [aws_security_group.sg.id]

  # AUTO INSTALL WEB SERVER
  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install httpd -y
              systemctl start httpd
              systemctl enable httpd
              echo "<h1>Web dari Terraform (Public Server)</h1>" > /var/www/html/index.html
              EOF

  tags = {
    Name = "terraform-public-server"
  }
}

# =====================
# EC2 PRIVATE SERVER
# =====================
resource "aws_instance" "private" {
  ami           = "ami-0df7a207adb9748c7"
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.private.id
  key_name      = "my-key"

  # ❗ TIDAK ADA PUBLIC IP
  vpc_security_group_ids = [aws_security_group.sg.id]

  tags = {
    Name = "terraform-private-server"
  }
}
