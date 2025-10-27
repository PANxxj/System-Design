# Infrastructure as Code (IaC) 🏗️

Master the art of defining and managing AWS infrastructure through code for repeatable, scalable deployments.

## 🎯 Learning Objectives

After completing this section, you'll be able to:
- Define infrastructure using code instead of manual console clicks
- Version control your infrastructure alongside application code
- Create repeatable, consistent environments (dev, staging, prod)
- Implement infrastructure best practices and security policies
- Automate deployment pipelines with IaC

## 📚 Prerequisites

**Required Completion**:
- [x] [AWS Fundamentals](../01-aws-fundamentals/) - Core AWS services
- [x] [Basic Web Application](../02-basic-web-application/) - Hands-on AWS experience

**Technical Skills**:
- Git version control
- Basic programming concepts (variables, functions, loops)
- YAML/JSON syntax understanding
- Command line proficiency

## ⏱️ Time Commitment

**Total Duration**: 4-5 weeks (25-30 hours)
- **Week 1**: CloudFormation basics (6-7 hours)
- **Week 2**: Terraform fundamentals (7-8 hours)
- **Week 3**: AWS CDK development (6-7 hours)
- **Week 4**: Advanced patterns and best practices (3-4 hours)
- **Week 5**: CI/CD integration (3-4 hours)

## 🛠️ IaC Tools Comparison

| Tool | Language | Learning Curve | Ecosystem | Best For |
|------|----------|---------------|-----------|----------|
| **CloudFormation** | YAML/JSON | Medium | AWS Native | AWS-only environments |
| **Terraform** | HCL | Medium-High | Multi-cloud | Multi-cloud, complex logic |
| **AWS CDK** | Python/JS/Java | High | AWS + Programming | Developers, complex apps |
| **Pulumi** | Any language | High | Multi-cloud | Full programming power |

## 🗂️ Section Contents

### 1. CloudFormation Mastery (Week 1)
- [CloudFormation Basics](cloudformation/basics.md)
- [Template Structure](cloudformation/template-structure.md)
- [Parameters and Outputs](cloudformation/parameters-outputs.md)
- [Nested Stacks](cloudformation/nested-stacks.md)
- [Custom Resources](cloudformation/custom-resources.md)

### 2. Terraform Fundamentals (Week 2)
- [Terraform Introduction](terraform/introduction.md)
- [Resource Management](terraform/resources.md)
- [State Management](terraform/state-management.md)
- [Modules and Composition](terraform/modules.md)
- [Multi-Environment Setup](terraform/environments.md)

### 3. AWS CDK Development (Week 3)
- [CDK Getting Started](cdk/getting-started.md)
- [Constructs and Stacks](cdk/constructs-stacks.md)
- [Higher-Level Constructs](cdk/high-level-constructs.md)
- [Testing CDK Code](cdk/testing.md)
- [CDK Pipelines](cdk/pipelines.md)

### 4. Best Practices & Patterns (Week 4)
- [Security by Default](best-practices/security.md)
- [Cost Optimization](best-practices/cost-optimization.md)
- [Naming Conventions](best-practices/naming.md)
- [Environment Management](best-practices/environments.md)
- [Disaster Recovery](best-practices/disaster-recovery.md)

### 5. CI/CD Integration (Week 5)
- [GitOps Workflows](best-practices/gitops.md)
- [Automated Testing](best-practices/testing.md)
- [Deployment Strategies](best-practices/deployment.md)
- [Monitoring IaC Changes](best-practices/monitoring.md)

## 🚀 Hands-on Projects

### Project 1: CloudFormation Web App (Week 1)
**Objective**: Recreate your basic web application using CloudFormation

**Components to Define**:
- VPC with public/private subnets
- Security groups and NACLs
- EC2 instances with Auto Scaling
- Application Load Balancer
- RDS database with Multi-AZ
- ElastiCache cluster
- CloudFront distribution

**Deliverables**:
- Complete CloudFormation templates
- Parameter files for different environments
- Deployment scripts and documentation

### Project 2: Terraform Multi-Environment (Week 2)
**Objective**: Build the same infrastructure with Terraform

**Advanced Features**:
- Terraform modules for reusability
- Remote state management with S3
- Environment-specific variable files
- Resource tagging strategies
- State locking with DynamoDB

**Deliverables**:
- Terraform modules for each component
- Environment configurations (dev/staging/prod)
- State management setup
- Automated apply/destroy scripts

### Project 3: CDK Application Stack (Week 3)
**Objective**: Use CDK to build a more complex application

**Features**:
- Higher-level constructs for common patterns
- Custom constructs for business logic
- Integration with existing AWS services
- Unit and integration tests
- CDK Pipeline for automated deployment

**Deliverables**:
- CDK application with multiple stacks
- Custom constructs library
- Comprehensive test suite
- Automated deployment pipeline

### Project 4: Enterprise IaC Solution (Week 4-5)
**Objective**: Build production-ready IaC with all best practices

**Requirements**:
- Multi-account AWS organization setup
- Cross-account role management
- Centralized logging and monitoring
- Automated security scanning
- Cost allocation and budgeting
- Disaster recovery procedures

**Deliverables**:
- Complete enterprise architecture
- Security and compliance documentation
- Operational runbooks
- Cost optimization reports

## 📋 Template Library

### CloudFormation Templates

#### Basic VPC Template
```yaml
# vpc-basic.yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Basic VPC with public and private subnets'

Parameters:
  VpcCidr:
    Type: String
    Default: '10.0.0.0/16'
    Description: 'CIDR block for VPC'

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !Ref VpcCidr
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-vpc'

  # Additional resources...
```

#### Auto Scaling Web App
```yaml
# web-app-autoscaling.yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Auto-scaling web application'

Parameters:
  InstanceType:
    Type: String
    Default: 't3.micro'
    AllowedValues: ['t3.micro', 't3.small', 't3.medium']

Resources:
  LaunchTemplate:
    Type: AWS::EC2::LaunchTemplate
    Properties:
      LaunchTemplateData:
        InstanceType: !Ref InstanceType
        SecurityGroupIds:
          - !Ref WebServerSecurityGroup
        UserData:
          Fn::Base64: !Sub |
            #!/bin/bash
            yum update -y
            yum install -y httpd
            systemctl start httpd
            systemctl enable httpd

  # Auto Scaling Group, Load Balancer, etc...
```

### Terraform Modules

#### VPC Module Structure
```hcl
# modules/vpc/main.tf
variable "cidr_block" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
}

resource "aws_vpc" "main" {
  cidr_block           = var.cidr_block
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "${var.name_prefix}-vpc"
    Environment = var.environment
  }
}

# Subnets, gateways, route tables...
```

#### Application Module
```hcl
# modules/web-app/main.tf
module "vpc" {
  source = "../vpc"

  cidr_block         = var.vpc_cidr
  availability_zones = var.availability_zones
  name_prefix        = var.name_prefix
  environment        = var.environment
}

module "compute" {
  source = "../compute"

  vpc_id               = module.vpc.vpc_id
  private_subnet_ids   = module.vpc.private_subnet_ids
  public_subnet_ids    = module.vpc.public_subnet_ids
  instance_type        = var.instance_type
  min_size            = var.min_instances
  max_size            = var.max_instances
}
```

### CDK Constructs

#### Basic Web Application Stack
```python
# app.py
from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_rds as rds,
    aws_elasticache as elasticache
)

class WebAppStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC
        vpc = ec2.Vpc(self, "WebAppVpc",
            max_azs=2,
            nat_gateways=1
        )

        # ECS Cluster
        cluster = ecs.Cluster(self, "WebAppCluster",
            vpc=vpc
        )

        # Application Load Balanced Service
        service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "WebAppService",
            cluster=cluster,
            memory_limit_mib=512,
            cpu=256,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_registry("nginx")
            )
        )

        # RDS Database
        database = rds.DatabaseInstance(self, "WebAppDatabase",
            engine=rds.DatabaseInstanceEngine.mysql(
                version=rds.MysqlEngineVersion.VER_8_0_28
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3,
                ec2.InstanceSize.MICRO
            ),
            vpc=vpc,
            multi_az=True,
            allocated_storage=20,
            storage_encrypted=True,
            deletion_protection=False
        )
```

## 🔄 Development Workflow

### 1. Development Cycle
```bash
# 1. Write/modify infrastructure code
vim main.tf

# 2. Plan changes
terraform plan

# 3. Apply changes to dev environment
terraform apply -var-file="dev.tfvars"

# 4. Test functionality
./test-infrastructure.sh

# 5. Commit to version control
git add . && git commit -m "Add RDS instance"

# 6. Deploy to staging via CI/CD
git push origin feature/add-database

# 7. Review and merge to main
# 8. Automatic deployment to production
```

### 2. Environment Promotion
```
Development → Staging → Production
     ↓           ↓         ↓
   Feature    Integration  Release
   Branch      Testing     Branch
     ↓           ↓         ↓
   Manual     Automated   Automated
   Deploy     Deploy      Deploy
```

### 3. Rollback Strategy
- Keep previous terraform state
- Version control for all changes
- Blue-green deployment patterns
- Database migration rollback plans
- Monitoring and alerting for issues

## 📊 Comparison Matrix

| Aspect | CloudFormation | Terraform | CDK |
|--------|---------------|-----------|-----|
| **Learning Curve** | Medium | Medium-High | High |
| **AWS Integration** | Excellent | Good | Excellent |
| **Multi-Cloud** | No | Yes | Limited |
| **State Management** | Built-in | External | Built-in |
| **Templating** | Limited | Good | Excellent |
| **Community** | AWS-focused | Large | Growing |
| **Debugging** | Limited | Good | Excellent |
| **Testing** | Manual | External tools | Built-in |
| **IDE Support** | Basic | Good | Excellent |
| **Cost** | Free | Free | Free |

## 💰 Cost Considerations

### IaC-Specific Costs
- **State Storage**: S3 buckets for Terraform state
- **CI/CD Pipeline**: CodePipeline, CodeBuild costs
- **Monitoring**: CloudWatch for infrastructure metrics
- **Security Scanning**: Third-party tools for IaC scanning

### Cost Optimization with IaC
- Resource tagging for cost allocation
- Automated resource cleanup
- Environment-specific sizing
- Scheduled start/stop for development resources
- Reserved instance automation

## 🔒 Security Best Practices

### Code Security
- Store sensitive values in AWS Secrets Manager
- Use IAM roles instead of access keys
- Implement least privilege access
- Scan IaC templates for security issues
- Version control all infrastructure changes

### Runtime Security
- Enable CloudTrail for all API calls
- Use AWS Config for compliance monitoring
- Implement security groups with minimal access
- Enable encryption at rest and in transit
- Regular security audits and penetration testing

## 📈 Monitoring and Observability

### Infrastructure Metrics
- Resource creation/modification/deletion events
- Deployment success/failure rates
- Infrastructure drift detection
- Cost tracking and anomaly detection
- Performance baselines and alerting

### Operational Dashboards
- Infrastructure health overview
- Deployment pipeline status
- Cost trends and optimization opportunities
- Security compliance status
- Resource utilization patterns

## 🎯 Success Criteria

You've mastered Infrastructure as Code when you can:
- [ ] Define complete AWS environments using code
- [ ] Implement CI/CD pipelines for infrastructure
- [ ] Manage multiple environments consistently
- [ ] Apply security and cost optimization best practices
- [ ] Troubleshoot and debug infrastructure issues
- [ ] Design reusable, modular infrastructure components

## 🚀 Next Steps

After mastering IaC:
1. **Implement in [Real-world Projects](../07-real-world-projects/)** - Apply IaC to complex applications
2. **Explore [Monitoring and Observability](../09-monitoring-observability/)** - Infrastructure monitoring
3. **Advance to [Cost Optimization](../10-cost-optimization/)** - Automated cost management

## 📞 Getting Help

### Common Issues
- **State Conflicts**: Terraform state locking issues
- **Permission Errors**: IAM role and policy problems
- **Resource Dependencies**: Circular dependency resolution
- **Template Errors**: YAML/JSON syntax and validation
- **Version Conflicts**: Tool and provider version mismatches

### Resources
- Official documentation for each tool
- Community templates and modules
- GitHub repositories with examples
- AWS workshops and tutorials
- Stack Overflow and community forums

---

**Ready to code your infrastructure?** Start with [CloudFormation Basics](cloudformation/) to begin your IaC journey!

*Remember: Infrastructure as Code is not just about automation—it's about creating reliable, repeatable, and scalable infrastructure that grows with your applications.*