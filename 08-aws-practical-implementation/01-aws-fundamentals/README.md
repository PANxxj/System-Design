# AWS Fundamentals - Getting Started 🚀

Master the core AWS services needed for system design implementation.

## 🎯 Learning Objectives

After completing this section, you'll be able to:
- Set up a secure AWS environment with proper IAM configuration
- Design and implement VPC networking architectures
- Choose and configure appropriate compute and storage services
- Apply AWS security best practices from day one

## 📚 Prerequisites

- [x] AWS account created (Free Tier recommended)
- [x] Basic understanding of networking concepts
- [x] Completed theoretical [fundamentals section](../../01-fundamentals/)
- [x] Command line familiarity

## ⏱️ Time Commitment

**Total Duration**: 2 weeks (12-15 hours)
- **Week 1**: Account setup, VPC, and basic services (6-8 hours)
- **Week 2**: Security, storage, and hands-on practice (6-7 hours)

## 🗂️ Section Contents

### 1. Account Setup & Security (Day 1-2)
- [Account Setup Guide](account-setup/)
- [AWS CLI Configuration](account-setup/cli-setup.md)
- [IAM Best Practices](security-iam/iam-fundamentals.md)
- [Billing Alerts & Cost Control](account-setup/cost-management.md)

### 2. VPC & Networking (Day 3-5)
- [VPC Fundamentals](vpc-networking/vpc-basics.md)
- [Subnets & Route Tables](vpc-networking/subnets-routing.md)
- [Security Groups & NACLs](vpc-networking/security-groups.md)
- [Internet & NAT Gateways](vpc-networking/gateways.md)

### 3. Compute Services (Day 6-8)
- [EC2 Instance Types & Selection](compute-storage/ec2-fundamentals.md)
- [Auto Scaling Basics](compute-storage/auto-scaling.md)
- [Load Balancer Types](compute-storage/load-balancers.md)
- [Lambda Introduction](compute-storage/lambda-basics.md)

### 4. Storage Services (Day 9-11)
- [S3 Storage Classes & Policies](compute-storage/s3-fundamentals.md)
- [EBS Volume Types](compute-storage/ebs-storage.md)
- [Database Options (RDS vs DynamoDB)](compute-storage/database-selection.md)

### 5. Security & Monitoring (Day 12-14)
- [Security Groups Deep Dive](security-iam/security-groups-advanced.md)
- [CloudWatch Basics](security-iam/cloudwatch-monitoring.md)
- [AWS Config & Compliance](security-iam/compliance-basics.md)

## 🛠️ Hands-on Labs

### Lab 1: Secure Account Setup (Day 1)
**Objective**: Configure a production-ready AWS account

**Tasks**:
- [ ] Create IAM user with MFA
- [ ] Set up billing alerts
- [ ] Configure AWS CLI with proper credentials
- [ ] Enable CloudTrail for audit logging

**Deliverable**: Secure AWS environment ready for development

### Lab 2: VPC Architecture (Day 3-4)
**Objective**: Build a 3-tier network architecture

**Tasks**:
- [ ] Create VPC with public/private subnets
- [ ] Configure route tables and gateways
- [ ] Set up security groups for web/app/database tiers
- [ ] Test connectivity between tiers

**Deliverable**: Production-ready VPC architecture diagram + implementation

### Lab 3: Web Server Deployment (Day 6-7)
**Objective**: Deploy and secure a web application

**Tasks**:
- [ ] Launch EC2 instances in appropriate subnets
- [ ] Configure security groups for HTTP/HTTPS access
- [ ] Set up Application Load Balancer
- [ ] Implement basic auto-scaling

**Deliverable**: Scalable web application infrastructure

### Lab 4: Database Integration (Day 9-10)
**Objective**: Add persistent storage layer

**Tasks**:
- [ ] Create RDS MySQL instance in private subnet
- [ ] Configure security groups for database access
- [ ] Set up backup and maintenance windows
- [ ] Connect web application to database

**Deliverable**: Complete 3-tier application with database

### Lab 5: Monitoring Setup (Day 12-13)
**Objective**: Implement comprehensive monitoring

**Tasks**:
- [ ] Configure CloudWatch metrics and alarms
- [ ] Set up log aggregation
- [ ] Create dashboards for key metrics
- [ ] Test alerting mechanisms

**Deliverable**: Production monitoring setup

## 💡 Key AWS Services to Master

### Core Networking
- **VPC**: Virtual Private Cloud for isolated environments
- **Subnets**: Public/private network segments
- **Route Tables**: Traffic routing configuration
- **Security Groups**: Instance-level firewalls
- **Internet Gateway**: Internet connectivity
- **NAT Gateway**: Outbound internet for private instances

### Essential Compute
- **EC2**: Virtual machines for applications
- **Auto Scaling Groups**: Automatic capacity management
- **Elastic Load Balancing**: Traffic distribution
- **Lambda**: Serverless compute functions

### Storage Solutions
- **S3**: Object storage for static content
- **EBS**: Block storage for EC2 instances
- **RDS**: Managed relational databases
- **DynamoDB**: NoSQL database service

### Security & Monitoring
- **IAM**: Identity and access management
- **CloudWatch**: Monitoring and logging
- **CloudTrail**: API call auditing
- **AWS Config**: Resource configuration tracking

## 📊 Progress Checklist

### Week 1: Foundation Setup
- [ ] **Account Security**
  - [ ] IAM user created with MFA enabled
  - [ ] Billing alerts configured
  - [ ] CloudTrail enabled for audit logging
  - [ ] AWS CLI configured and tested

- [ ] **Network Architecture**
  - [ ] VPC created with proper CIDR blocks
  - [ ] Public/private subnets in multiple AZs
  - [ ] Route tables configured correctly
  - [ ] Security groups follow least privilege principle

### Week 2: Services Integration
- [ ] **Compute Resources**
  - [ ] EC2 instances launched and configured
  - [ ] Load balancer distributing traffic
  - [ ] Auto scaling group responding to load
  - [ ] Lambda function processing events

- [ ] **Storage & Database**
  - [ ] S3 bucket with proper policies
  - [ ] RDS instance in private subnet
  - [ ] EBS volumes attached and configured
  - [ ] Database connectivity tested

- [ ] **Monitoring & Security**
  - [ ] CloudWatch dashboards created
  - [ ] Alarms configured for key metrics
  - [ ] Security groups audited and optimized
  - [ ] Backup strategies implemented

## 🔗 Integration with System Design Theory

### Mapping Concepts to AWS
| System Design Concept | AWS Implementation |
|----------------------|-------------------|
| **Horizontal Scaling** | Auto Scaling Groups + Load Balancers |
| **Load Distribution** | Application/Network Load Balancers |
| **Data Persistence** | RDS Multi-AZ + EBS + S3 |
| **Caching** | ElastiCache (covered in later sections) |
| **Security** | VPC + Security Groups + IAM |
| **Monitoring** | CloudWatch + CloudTrail + X-Ray |
| **Fault Tolerance** | Multi-AZ deployment + Auto Scaling |

### Real-world Application
- **Single Points of Failure**: Eliminated through Multi-AZ deployment
- **Scalability**: Achieved through Auto Scaling and Load Balancing
- **Security**: Implemented through VPC isolation and Security Groups
- **Cost Optimization**: Managed through right-sizing and monitoring

## 🎯 Success Criteria

You've mastered AWS fundamentals when you can:
- [ ] Design secure, scalable VPC architectures
- [ ] Choose appropriate compute/storage services for given requirements
- [ ] Implement proper security controls and monitoring
- [ ] Estimate costs and optimize resource usage
- [ ] Deploy applications following AWS best practices

## 🚀 Next Steps

After completing AWS fundamentals:
1. **Move to [Basic Web Application](../02-basic-web-application/)** - Apply these concepts in a real project
2. **Review [Scalability Basics](../../01-fundamentals/scalability-basics.md)** - Connect theory with AWS implementation
3. **Practice with [Real-world Projects](../07-real-world-projects/)** - Build portfolio projects

## 📞 Getting Help

- **AWS Documentation**: Comprehensive service guides
- **AWS Free Tier**: Monitor usage to avoid charges
- **AWS Training**: Free digital courses available
- **Community**: AWS re:Post and Stack Overflow

---

**Ready to start?** Begin with [Account Setup](account-setup/) to configure your AWS environment!

*Remember: Always follow the principle of least privilege and clean up resources after experiments.*