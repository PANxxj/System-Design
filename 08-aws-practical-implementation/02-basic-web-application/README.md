# Basic Web Application on AWS 🌐

Build your first scalable web application using AWS services, applying system design fundamentals.

## 🎯 Learning Objectives

After completing this section, you'll be able to:
- Deploy a 3-tier web application on AWS
- Implement load balancing and auto-scaling
- Configure databases with high availability
- Set up monitoring and alerting
- Apply security best practices

## 📚 Prerequisites

**Required Completion**:
- [x] [AWS Fundamentals](../01-aws-fundamentals/) - VPC, EC2, RDS basics
- [x] [System Design Fundamentals](../../01-fundamentals/) - Scalability concepts

**Technical Skills**:
- Basic web development (HTML, CSS, JavaScript)
- Server-side programming (Python/Node.js/Java)
- Database concepts (SQL)
- Linux command line basics

## ⏱️ Time Commitment

**Total Duration**: 3-4 weeks (20-25 hours)
- **Week 1**: Single instance deployment (5-6 hours)
- **Week 2**: Load balancing and scaling (6-7 hours)
- **Week 3**: Database integration and optimization (6-7 hours)
- **Week 4**: Monitoring, security, and optimization (3-5 hours)

## 🏗️ Architecture Evolution

### Phase 1: Single Instance (Week 1)
```
Internet → EC2 Instance (Web + App + DB)
```

### Phase 2: Load Balanced (Week 2)
```
Internet → ALB → [EC2-1, EC2-2] → RDS
```

### Phase 3: Auto Scaling (Week 3)
```
Internet → CloudFront → ALB → Auto Scaling Group → RDS Multi-AZ
                               ↓
                           ElastiCache
```

### Phase 4: Production Ready (Week 4)
```
Internet → Route 53 → CloudFront → ALB → Auto Scaling Group → RDS Aurora
                                    ↓              ↓
                              ElastiCache    CloudWatch
```

## 🗂️ Section Contents

### Week 1: Single Instance Deployment
- [Application Setup](single-instance/app-setup.md)
- [EC2 Configuration](single-instance/ec2-deployment.md)
- [Domain and SSL](single-instance/domain-ssl.md)
- [Basic Security](single-instance/security-basics.md)

### Week 2: Load Balancing & Scaling
- [Application Load Balancer](load-balanced/alb-setup.md)
- [Multi-Instance Deployment](load-balanced/multi-instance.md)
- [Health Checks](load-balanced/health-checks.md)
- [Session Management](load-balanced/session-management.md)

### Week 3: Database Integration
- [RDS Setup](database-integration/rds-configuration.md)
- [Connection Pooling](database-integration/connection-pooling.md)
- [Read Replicas](database-integration/read-replicas.md)
- [Backup Strategies](database-integration/backup-restore.md)

### Week 4: Production Readiness
- [Auto Scaling Groups](production-ready/auto-scaling.md)
- [CloudFront CDN](production-ready/cdn-setup.md)
- [Monitoring Setup](production-ready/monitoring.md)
- [Cost Optimization](production-ready/cost-optimization.md)

## 🛠️ Hands-on Labs

### Lab 1: Deploy Simple Web App (Week 1)
**Objective**: Get a basic web application running on AWS

**Application**: Simple blog/todo app with basic CRUD operations

**Tasks**:
- [ ] Create EC2 instance with security group
- [ ] Install web server (Nginx/Apache) and application runtime
- [ ] Deploy application code
- [ ] Configure domain with Route 53
- [ ] Set up SSL certificate with ACM

**Deliverable**: Working web application accessible via custom domain

### Lab 2: Add Load Balancing (Week 2)
**Objective**: Distribute traffic across multiple instances

**Tasks**:
- [ ] Create Application Load Balancer
- [ ] Launch multiple EC2 instances
- [ ] Configure target groups and health checks
- [ ] Implement session persistence
- [ ] Test failover scenarios

**Deliverable**: Highly available web application with load balancing

### Lab 3: Database Layer (Week 3)
**Objective**: Separate database layer with high availability

**Tasks**:
- [ ] Create RDS MySQL instance with Multi-AZ
- [ ] Migrate application to use RDS
- [ ] Set up read replicas for performance
- [ ] Configure automated backups
- [ ] Implement connection pooling

**Deliverable**: Scalable application with managed database

### Lab 4: Auto Scaling & CDN (Week 4)
**Objective**: Implement automatic scaling and global content delivery

**Tasks**:
- [ ] Create Auto Scaling Group with policies
- [ ] Set up CloudFront distribution
- [ ] Configure CloudWatch alarms
- [ ] Implement comprehensive monitoring
- [ ] Optimize for cost and performance

**Deliverable**: Production-ready, globally distributed web application

## 📋 Sample Application Options

### Option 1: Personal Blog Platform
**Features**:
- User registration and authentication
- Blog post creation and editing
- Comment system
- File upload for images
- Search functionality

**AWS Services**:
- EC2 for web servers
- RDS for user data and posts
- S3 for image storage
- ElastiCache for session storage
- CloudFront for static content

### Option 2: Task Management System
**Features**:
- User accounts and teams
- Project and task management
- Real-time collaboration
- File attachments
- Reporting dashboard

**AWS Services**:
- ECS for containerized deployment
- Aurora for transactional data
- ElastiCache for real-time features
- S3 for file storage
- SQS for background processing

### Option 3: E-commerce Storefront
**Features**:
- Product catalog
- Shopping cart
- Order processing
- Payment integration
- Inventory management

**AWS Services**:
- Auto Scaling for variable load
- RDS for product and order data
- ElastiCache for cart sessions
- S3 for product images
- SQS for order processing

## 🔧 Technology Stack Options

### Frontend Options
- **Static**: HTML, CSS, JavaScript (served from S3/CloudFront)
- **React/Vue**: Single Page Application with API backend
- **Server-Rendered**: Traditional server-side rendering

### Backend Options
- **Python**: Django/Flask with Gunicorn
- **Node.js**: Express.js with PM2
- **Java**: Spring Boot with embedded Tomcat
- **PHP**: Laravel with PHP-FPM

### Database Options
- **Relational**: RDS MySQL/PostgreSQL
- **NoSQL**: DynamoDB for simple key-value needs
- **Cache**: ElastiCache Redis for sessions and caching

## 📊 Performance Targets

### Week 1 Goals (Single Instance)
- [ ] **Response Time**: < 2 seconds for page loads
- [ ] **Uptime**: 99% availability
- [ ] **Capacity**: Handle 100 concurrent users
- [ ] **Security**: Basic security groups and SSL

### Week 2 Goals (Load Balanced)
- [ ] **Response Time**: < 1 second for page loads
- [ ] **Uptime**: 99.5% availability with failover
- [ ] **Capacity**: Handle 500 concurrent users
- [ ] **Scalability**: Manual scaling to multiple instances

### Week 3 Goals (Database Integration)
- [ ] **Response Time**: < 800ms with database queries
- [ ] **Uptime**: 99.9% with Multi-AZ database
- [ ] **Capacity**: Handle 1000 concurrent users
- [ ] **Data Persistence**: Automated backups and recovery

### Week 4 Goals (Production Ready)
- [ ] **Response Time**: < 500ms globally with CDN
- [ ] **Uptime**: 99.9% with auto-scaling
- [ ] **Capacity**: Auto-scale from 2-10 instances
- [ ] **Monitoring**: Full observability and alerting

## 💰 Cost Estimation

### Week 1 (Single Instance)
- **EC2 t3.small**: $15/month
- **RDS db.t3.micro**: $15/month
- **Route 53**: $1/month
- **Total**: ~$31/month

### Week 2-3 (Load Balanced)
- **EC2 instances (2x t3.small)**: $30/month
- **Application Load Balancer**: $20/month
- **RDS db.t3.small Multi-AZ**: $30/month
- **Total**: ~$80/month

### Week 4 (Production Ready)
- **Auto Scaling (2-4 instances)**: $30-60/month
- **ALB + CloudFront**: $25/month
- **RDS + ElastiCache**: $40/month
- **Total**: ~$95-125/month

### Cost Optimization Tips
- Use Spot Instances for development
- Right-size instances based on monitoring
- Implement lifecycle policies for logs
- Use Reserved Instances for predictable workloads

## 🔒 Security Checklist

### Network Security
- [ ] VPC with public/private subnets
- [ ] Security groups with least privilege
- [ ] NACLs for additional protection
- [ ] WAF for application-level protection

### Instance Security
- [ ] Regular security updates
- [ ] SSH key-based authentication only
- [ ] Disable unnecessary services
- [ ] Implement fail2ban for brute force protection

### Database Security
- [ ] Database in private subnet only
- [ ] Encrypted at rest and in transit
- [ ] Regular security patches
- [ ] Database activity monitoring

### Application Security
- [ ] SSL/TLS for all communications
- [ ] Input validation and sanitization
- [ ] Session management best practices
- [ ] Regular security scanning

## 📈 Monitoring Strategy

### Key Metrics to Track
- **Response Time**: Application performance
- **Error Rate**: Application reliability
- **CPU/Memory**: Resource utilization
- **Database Performance**: Query performance and connections
- **Network**: Data transfer and latency

### CloudWatch Alarms
- High CPU utilization (>80%)
- High memory usage (>85%)
- Application errors (>5%)
- Database connection failures
- Load balancer unhealthy targets

### Custom Dashboards
- Application performance overview
- Infrastructure health status
- Cost monitoring and trends
- User activity and engagement

## 🎯 Success Criteria

You've successfully completed this section when you can:
- [ ] Deploy a multi-tier web application on AWS
- [ ] Implement auto-scaling based on demand
- [ ] Configure monitoring and alerting
- [ ] Apply security best practices
- [ ] Optimize for cost and performance
- [ ] Troubleshoot common issues

## 🚀 Next Steps

After completing the basic web application:
1. **Advance to [Scalable Architectures](../03-scalable-architectures/)** - Learn advanced scaling patterns
2. **Explore [Microservices Implementation](../04-microservices-implementation/)** - Break down into smaller services
3. **Try [Real-world Projects](../07-real-world-projects/)** - Apply skills to complex scenarios

## 📞 Getting Help

### Common Issues and Solutions
- **Instance Connection Issues**: Check security groups and key pairs
- **Database Connection Failures**: Verify security groups and connection strings
- **Load Balancer Health Checks**: Review target group configurations
- **SSL Certificate Issues**: Validate domain ownership and DNS configuration

### Resources
- AWS Documentation for each service
- CloudFormation templates for infrastructure
- Sample application code repositories
- Community forums and Stack Overflow

---

**Ready to build?** Start with [Single Instance Deployment](single-instance/) to create your first AWS web application!

*Remember: Start simple and iterate. Each week builds upon the previous work to create a production-ready application.*