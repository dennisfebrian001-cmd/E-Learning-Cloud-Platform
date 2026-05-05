# E-Learning Cloud Platform

## Deskripsi
E-Learning Cloud Platform adalah aplikasi pembelajaran online berbasis cloud yang dibangun menggunakan layanan AWS. Platform ini dirancang untuk menyediakan sistem pembelajaran yang scalable, secure, dan highly available dengan memanfaatkan arsitektur modern cloud.

## Arsitektur
Arsitektur yang digunakan terdiri dari beberapa komponen utama:

- EC2 (Elastic Compute Cloud)
  Menjalankan backend aplikasi (server utama)
- RDS (Relational Database Service)
  Menyimpan data pengguna, materi, dan aktivitas
- S3 (Simple Storage Service)
  Penyimpanan file seperti video dan materi pembelajaran
- CloudFront (CDN)
  Mempercepat distribusi konten ke pengguna
- Load Balancer (ALB)
  Mendistribusikan traffic ke beberapa instance untuk high availability

## Teknologi yang Digunakan
- Amazon Web Services (AWS)
- Terraform (Infrastructure as Code)
- MySQL (RDS)
- Amazon Linux (EC2)

## Infrastruktur
- VPC dengan public & private subnet
- Bastion host untuk akses SSH
- Private EC2 untuk aplikasi
- RDS di private subnet (secure)
- NAT Gateway untuk akses internet dari private subnet
- IAM Role untuk keamanan akses

## Fitur
- Login/Register
- Upload materi
- Streaming video

## Cara Deployment
# Clone repository
git clone https://github.com/username/e-learning-cloud.git
cd e-learning-cloud

# Inisialisasi Terraform
terraform init

# Preview perubahan
terraform plan

# Deploy infrastructure
terraform apply

## Anggota
- Martin Ariai
- Athaya Muluq Priadinata
- Exka Julianto
- Dennis Febrian
