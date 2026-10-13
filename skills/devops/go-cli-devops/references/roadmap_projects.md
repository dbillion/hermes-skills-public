# Official roadmap.sh DevOps Projects (26 total)

Extracted 2026-08-11 via browser (JS-rendered page; API 404s). Canonical requirement
source for the devops-go rebuild. Map each to a Go/GCP implementation.

## Beginner (11)
B1 CLI Server Performance Stats
B2 CLI Log Archive Tool
B3 CLI Nginx Log Analyser
B4 GitHub Pages Deployment
B5 SSH Remote Server Setup
B6 Static Site Server Setup
B7 Basic DNS Setup
B8 Simple Monitoring (Netdata)
B9 Dummy Systemd Service
B10 Basic Dockerfile
B11 EC2 Instance

## Intermediate (11)
I1 Pomodoro Timer
I2 Ansible Configuration Management
I3 Terraform IaC on DigitalOcean
I4 Node.js Service Deployment (GH Actions)
I5 Dockerized Service (GH Actions)
I6 Docker Compose Multi-Container
I7 Automated DB Backups
I8 Bastion Host
I9 File Integrity Checker
I10 Linux Server Setup
I11 VPN Server Setup

## Advanced (4)
A1 Blue-Green Deployment
A2 Prometheus + Grafana
A3 Multi-Service Docker
A4 Service Discovery (Consul)

## Notes
- The roadmap page renders 26 (not 30). Earlier "30" count was wrong.
- Go/GCP mapping: Terraform->Terraform google provider; Jenkins->GH Actions/Cloud Build;
  K8s/Docker->GKE/Cloud Run. Ansible has no GCP-native equivalent (note deviation).
- Implemented so far: B1, B2, B3 (cobra CLIs), B10/P01 (Cloud Run deploy+teardown).
