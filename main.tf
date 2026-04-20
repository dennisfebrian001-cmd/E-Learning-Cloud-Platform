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
# Subnet (public)
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
# Internet Gateway
# =====================
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "terraform-igw"
  }
}

# =====================
# Route Table
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

# Hubungkan subnet ke route table
resource "aws_route_table_association" "assoc" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.rt.id
}

# =====================
# Security Group
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
# EC2 Instance
# =====================
resource "aws_instance" "public" {
  ami           = "ami-0df7a207adb9748c7"
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.public.id
  key_name      = "my-key"

  associate_public_ip_address = true

  vpc_security_group_ids = [aws_security_group.sg.id]

  # 🔥 AUTO INSTALL WEB SERVER
  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install httpd -y
              systemctl start httpd
              systemctl enable httpd
              echo "<h1>Web dari Terraform</h1>" > /var/www/html/index.html
              EOF

  tags = {
    Name = "terraform-public-server"
  }
}