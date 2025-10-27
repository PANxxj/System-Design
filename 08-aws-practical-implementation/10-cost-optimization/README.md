# Cost Optimization on AWS 💰

Master advanced cost optimization strategies and implement cost-effective architectures for sustainable AWS operations.

## 🎯 Learning Objectives

After completing this section, you'll be able to:
- Implement comprehensive cost optimization strategies
- Design cost-aware architectures from the ground up
- Set up automated cost monitoring and governance
- Optimize resource utilization across all AWS services
- Build cost-effective scaling strategies

## 📚 Prerequisites

**Required Completion**:
- [x] [AWS Fundamentals](../01-aws-fundamentals/) - Core AWS services understanding
- [x] [Scalable Architectures](../03-scalable-architectures/) - Resource optimization concepts
- [x] [Monitoring and Observability](../09-monitoring-observability/) - Cost tracking basics

**Technical Skills**:
- Understanding of AWS pricing models
- Experience with CloudWatch and monitoring
- Basic knowledge of automation and scripting
- Familiarity with resource tagging strategies

## ⏱️ Time Commitment

**Total Duration**: 3-4 weeks (18-22 hours)
- **Week 1**: Cost analysis and right-sizing (5-6 hours)
- **Week 2**: Reserved instances and savings plans (5-6 hours)
- **Week 3**: Automated optimization and governance (4-5 hours)
- **Week 4**: Advanced optimization strategies (4-5 hours)

## 💡 Cost Optimization Principles

### The 5 Pillars of Cost Optimization
```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   RIGHT SIZE    │  │   ELASTICITY    │  │   PURCHASING    │
│                 │  │                 │  │                 │
│ • Match capacity│  │ • Scale on      │  │ • Reserved      │
│   to demand     │  │   demand        │  │   Instances     │
│ • Monitor       │  │ • Auto Scaling  │  │ • Savings Plans │
│   utilization   │  │ • Spot Instances│  │ • Volume        │
│                 │  │                 │  │   Discounts     │
└─────────────────┘  └─────────────────┘  └─────────────────┘

┌─────────────────┐  ┌─────────────────┐
│   MEASURE &     │  │   OPTIMIZE      │
│   MONITOR       │  │   OVER TIME     │
│                 │  │                 │
│ • Cost Explorer │  │ • Regular       │
│ • Budgets       │  │   Reviews       │
│ • Anomaly       │  │ • Architecture  │
│   Detection     │  │   Evolution     │
│                 │  │ • New Services  │
└─────────────────┘  └─────────────────┘
```

### Cost Optimization Maturity Model
```
Level 1: Basic Awareness
├── Cost tracking enabled
├── Basic tagging implemented
├── Manual right-sizing
└── Monthly cost reviews

Level 2: Proactive Management
├── Automated monitoring
├── Reserved Instance planning
├── Scheduled scaling
└── Cost anomaly detection

Level 3: Advanced Optimization
├── Spot Instance integration
├── Multi-account governance
├── Automated rightsizing
└── Predictive analytics

Level 4: Cost Innovation
├── FinOps culture
├── Real-time optimization
├── Advanced automation
└── Cost-driven architecture
```

## 🗂️ Section Contents

### Week 1: Cost Analysis & Right-Sizing
- [Cost Analysis Fundamentals](resource-optimization/cost-analysis.md)
- [EC2 Right-Sizing](resource-optimization/ec2-rightsizing.md)
- [Database Optimization](resource-optimization/database-optimization.md)
- [Storage Cost Optimization](resource-optimization/storage-optimization.md)

### Week 2: Purchasing Optimization
- [Reserved Instance Strategy](reserved-instances/ri-strategy.md)
- [Savings Plans Implementation](reserved-instances/savings-plans.md)
- [Spot Instance Integration](spot-instances/spot-strategy.md)
- [Volume Discount Planning](reserved-instances/volume-discounts.md)

### Week 3: Automated Optimization
- [Cost Anomaly Detection](cost-monitoring/anomaly-detection.md)
- [Automated Scaling Policies](cost-monitoring/auto-scaling-cost.md)
- [Resource Tagging Governance](cost-monitoring/tagging-strategy.md)
- [Budget Automation](cost-monitoring/budget-automation.md)

### Week 4: Advanced Strategies
- [Multi-Account Cost Management](advanced-strategies/multi-account.md)
- [FinOps Implementation](advanced-strategies/finops.md)
- [Cost-Aware Development](advanced-strategies/cost-aware-dev.md)
- [Sustainability and Green Computing](advanced-strategies/sustainability.md)

## 🛠️ Hands-on Labs

### Lab 1: Complete Cost Assessment (Week 1)
**Objective**: Analyze current AWS spending and identify optimization opportunities

**Assessment Areas**:
- EC2 instances utilization analysis
- Storage usage patterns and lifecycle
- Database performance vs cost
- Network data transfer costs
- Unused and underutilized resources

**Tools and Techniques**:
```python
# Cost analysis automation script
import boto3
import pandas as pd
from datetime import datetime, timedelta

class CostAnalyzer:
    def __init__(self):
        self.ce_client = boto3.client('ce')
        self.ec2_client = boto3.client('ec2')
        self.cloudwatch = boto3.client('cloudwatch')

    def analyze_ec2_utilization(self):
        """Analyze EC2 instance utilization vs cost"""

        # Get EC2 costs for last 30 days
        costs = self.ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                'End': datetime.now().strftime('%Y-%m-%d')
            },
            Granularity='MONTHLY',
            Metrics=['BlendedCost'],
            GroupBy=[
                {'Type': 'DIMENSION', 'Key': 'RESOURCE_ID'}
            ],
            Filter={
                'Dimensions': {
                    'Key': 'SERVICE',
                    'Values': ['Amazon Elastic Compute Cloud - Compute']
                }
            }
        )

        # Get instance details
        instances = self.ec2_client.describe_instances()

        recommendations = []

        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                instance_type = instance['InstanceType']

                # Get CPU utilization
                cpu_metrics = self.cloudwatch.get_metric_statistics(
                    Namespace='AWS/EC2',
                    MetricName='CPUUtilization',
                    Dimensions=[
                        {'Name': 'InstanceId', 'Value': instance_id}
                    ],
                    StartTime=datetime.now() - timedelta(days=30),
                    EndTime=datetime.now(),
                    Period=3600,
                    Statistics=['Average']
                )

                if cpu_metrics['Datapoints']:
                    avg_cpu = sum(dp['Average'] for dp in cpu_metrics['Datapoints']) / len(cpu_metrics['Datapoints'])

                    # Recommend downsizing if consistently low utilization
                    if avg_cpu < 20:
                        recommendations.append({
                            'instance_id': instance_id,
                            'current_type': instance_type,
                            'avg_cpu': avg_cpu,
                            'recommendation': 'Consider downsizing or using burstable instances',
                            'potential_savings': self.calculate_savings(instance_type)
                        })

        return recommendations

    def analyze_storage_costs(self):
        """Analyze storage usage and recommend optimizations"""

        s3_client = boto3.client('s3')
        buckets = s3_client.list_buckets()

        storage_analysis = []

        for bucket in buckets['Buckets']:
            bucket_name = bucket['Name']

            # Get bucket size metrics
            try:
                size_metrics = self.cloudwatch.get_metric_statistics(
                    Namespace='AWS/S3',
                    MetricName='BucketSizeBytes',
                    Dimensions=[
                        {'Name': 'BucketName', 'Value': bucket_name},
                        {'Name': 'StorageType', 'Value': 'StandardStorage'}
                    ],
                    StartTime=datetime.now() - timedelta(days=1),
                    EndTime=datetime.now(),
                    Period=86400,
                    Statistics=['Average']
                )

                if size_metrics['Datapoints']:
                    bucket_size = size_metrics['Datapoints'][-1]['Average']

                    # Check lifecycle policies
                    try:
                        s3_client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
                        has_lifecycle = True
                    except:
                        has_lifecycle = False

                    storage_analysis.append({
                        'bucket_name': bucket_name,
                        'size_gb': bucket_size / (1024**3),
                        'has_lifecycle_policy': has_lifecycle,
                        'recommendation': 'Implement lifecycle policy' if not has_lifecycle else 'Review lifecycle rules'
                    })

            except Exception as e:
                print(f"Error analyzing bucket {bucket_name}: {e}")

        return storage_analysis

    def calculate_savings(self, instance_type):
        """Calculate potential savings from right-sizing"""
        # Simplified calculation - in reality, you'd use AWS Pricing API
        pricing_map = {
            't3.large': 0.0832,
            't3.medium': 0.0416,
            't3.small': 0.0208,
            'm5.large': 0.096,
            'm5.medium': 0.048
        }

        current_cost = pricing_map.get(instance_type, 0)

        # Suggest one size smaller
        if instance_type in ['t3.large', 'm5.large']:
            smaller_type = instance_type.replace('large', 'medium')
            smaller_cost = pricing_map.get(smaller_type, current_cost)
            return (current_cost - smaller_cost) * 24 * 30  # Monthly savings

        return 0
```

### Lab 2: Reserved Instance Optimization (Week 2)
**Objective**: Implement comprehensive RI and Savings Plans strategy

**Implementation Steps**:
1. Historical usage analysis
2. RI coverage gap identification
3. Savings Plans vs RI comparison
4. Automated RI management setup

**RI Optimization Strategy**:
```python
class ReservedInstanceOptimizer:
    def __init__(self):
        self.ce_client = boto3.client('ce')
        self.ec2_client = boto3.client('ec2')

    def analyze_ri_opportunities(self):
        """Identify RI purchase opportunities"""

        # Get RI coverage for last 3 months
        coverage = self.ce_client.get_reservation_coverage(
            TimePeriod={
                'Start': (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d'),
                'End': datetime.now().strftime('%Y-%m-%d')
            },
            GroupBy=[
                {'Type': 'DIMENSION', 'Key': 'INSTANCE_TYPE'}
            ]
        )

        # Get RI recommendations
        recommendations = self.ce_client.get_reservation_purchase_recommendation(
            Service='Amazon Elastic Compute Cloud - Compute',
            PaymentOption='PARTIAL_UPFRONT',
            TermInYears='ONE_YEAR',
            LookbackPeriodInDays='SIXTY_DAYS'
        )

        optimization_plan = []

        for rec in recommendations['Recommendations']:
            instance_details = rec['InstanceDetails']['EC2InstanceDetails']

            optimization_plan.append({
                'instance_type': instance_details['InstanceType'],
                'availability_zone': instance_details['AvailabilityZone'],
                'recommended_instances': rec['RecommendationDetails']['RecommendedNumberOfInstancesToPurchase'],
                'estimated_monthly_savings': rec['RecommendationDetails']['EstimatedMonthlySavingsAmount'],
                'upfront_cost': rec['RecommendationDetails']['UpfrontCost'],
                'break_even_months': rec['RecommendationDetails']['BreakEvenInMonths']
            })

        return optimization_plan

    def implement_auto_ri_management(self):
        """Set up automated RI management"""

        # Create Lambda function for RI monitoring
        lambda_code = """
import boto3
import json

def lambda_handler(event, context):
    ce_client = boto3.client('ce')

    # Check RI utilization
    utilization = ce_client.get_reservation_utilization(
        TimePeriod={
            'Start': '2024-01-01',
            'End': '2024-01-31'
        }
    )

    # Alert if utilization is low
    total_utilization = float(utilization['Total']['UtilizationPercentage'])

    if total_utilization < 80:
        # Send alert
        sns = boto3.client('sns')
        message = f"RI Utilization Alert: {total_utilization}% - Consider modification or exchange"

        sns.publish(
            TopicArn=os.environ['ALERT_TOPIC_ARN'],
            Message=message,
            Subject='Reserved Instance Utilization Alert'
        )

    return {'statusCode': 200}
"""

        # Create CloudWatch event rule for monthly checks
        events_rule = {
            'Name': 'RIUtilizationCheck',
            'ScheduleExpression': 'rate(30 days)',
            'State': 'ENABLED',
            'Description': 'Monthly RI utilization check'
        }

        return {
            'lambda_function': lambda_code,
            'cloudwatch_rule': events_rule
        }
```

### Lab 3: Spot Instance Integration (Week 2-3)
**Objective**: Implement cost-effective Spot Instance strategies

**Spot Integration Patterns**:
- Batch processing workloads
- Development/testing environments
- Fault-tolerant web applications
- CI/CD pipeline workers

**Spot Fleet Implementation**:
```python
class SpotInstanceManager:
    def __init__(self):
        self.ec2_client = boto3.client('ec2')
        self.autoscaling_client = boto3.client('autoscaling')

    def create_mixed_instance_asg(self):
        """Create Auto Scaling Group with mixed On-Demand and Spot instances"""

        launch_template = {
            'LaunchTemplateName': 'mixed-instance-template',
            'LaunchTemplateData': {
                'ImageId': 'ami-0abcdef1234567890',
                'SecurityGroupIds': ['sg-12345678'],
                'UserData': base64.b64encode("""#!/bin/bash
                    yum update -y
                    yum install -y docker
                    service docker start
                    usermod -a -G docker ec2-user
                """.encode()).decode(),
                'TagSpecifications': [
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {'Key': 'Name', 'Value': 'MixedInstance'},
                            {'Key': 'Environment', 'Value': 'Production'},
                            {'Key': 'CostOptimization', 'Value': 'SpotEnabled'}
                        ]
                    }
                ]
            }
        }

        # Create launch template
        self.ec2_client.create_launch_template(**launch_template)

        # Create mixed instances Auto Scaling Group
        asg_config = {
            'AutoScalingGroupName': 'mixed-instance-asg',
            'MinSize': 2,
            'MaxSize': 20,
            'DesiredCapacity': 4,
            'VPCZoneIdentifier': 'subnet-12345,subnet-67890',
            'MixedInstancesPolicy': {
                'LaunchTemplate': {
                    'LaunchTemplateSpecification': {
                        'LaunchTemplateName': 'mixed-instance-template',
                        'Version': '$Latest'
                    },
                    'Overrides': [
                        {'InstanceType': 't3.medium', 'AvailabilityZone': 'us-east-1a'},
                        {'InstanceType': 't3.large', 'AvailabilityZone': 'us-east-1b'},
                        {'InstanceType': 'm5.medium', 'AvailabilityZone': 'us-east-1a'},
                        {'InstanceType': 'm5.large', 'AvailabilityZone': 'us-east-1b'}
                    ]
                },
                'InstancesDistribution': {
                    'OnDemandAllocationStrategy': 'prioritized',
                    'OnDemandBaseCapacity': 2,
                    'OnDemandPercentageAboveBaseCapacity': 25,
                    'SpotAllocationStrategy': 'diversified',
                    'SpotInstancePools': 4,
                    'SpotMaxPrice': '0.05'
                }
            }
        }

        self.autoscaling_client.create_auto_scaling_group(**asg_config)

    def implement_spot_interruption_handling(self):
        """Handle Spot instance interruptions gracefully"""

        user_data_script = """#!/bin/bash
# Install spot interruption handler
curl -O https://aws-ec2-spot-labs.s3.amazonaws.com/aws-ec2-spot-interruption-handler/spot-interruption-handler.sh
chmod +x spot-interruption-handler.sh

# Set up monitoring script
cat > /opt/spot-monitor.sh << 'EOF'
#!/bin/bash
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

while true; do
    INTERRUPTION=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" -s http://169.254.169.254/latest/meta-data/spot/instance-action)

    if [ $? -eq 0 ]; then
        echo "Spot interruption notice received: $INTERRUPTION"

        # Graceful shutdown procedures
        # Stop accepting new requests
        systemctl stop nginx

        # Drain existing connections
        sleep 30

        # Stop application
        systemctl stop application

        # Clean up temporary files
        rm -rf /tmp/app-*

        break
    fi

    sleep 5
done
EOF

chmod +x /opt/spot-monitor.sh
nohup /opt/spot-monitor.sh > /var/log/spot-monitor.log 2>&1 &
"""

        return user_data_script

    def optimize_spot_pricing(self):
        """Analyze spot pricing history for optimization"""

        # Get spot price history
        response = self.ec2_client.describe_spot_price_history(
            InstanceTypes=['t3.medium', 't3.large', 'm5.medium', 'm5.large'],
            ProductDescriptions=['Linux/UNIX'],
            StartTime=datetime.now() - timedelta(days=7),
            EndTime=datetime.now()
        )

        price_analysis = {}

        for price_point in response['SpotPrices']:
            instance_type = price_point['InstanceType']
            az = price_point['AvailabilityZone']
            price = float(price_point['SpotPrice'])

            key = f"{instance_type}_{az}"
            if key not in price_analysis:
                price_analysis[key] = []
            price_analysis[key].append(price)

        # Calculate statistics for each instance type/AZ combination
        recommendations = []

        for key, prices in price_analysis.items():
            instance_type, az = key.split('_')
            avg_price = sum(prices) / len(prices)
            max_price = max(prices)
            min_price = min(prices)

            recommendations.append({
                'instance_type': instance_type,
                'availability_zone': az,
                'avg_spot_price': avg_price,
                'max_spot_price': max_price,
                'min_spot_price': min_price,
                'price_volatility': (max_price - min_price) / avg_price,
                'recommended_max_bid': avg_price * 1.2  # 20% above average
            })

        return sorted(recommendations, key=lambda x: x['avg_spot_price'])
```

### Lab 4: Automated Cost Governance (Week 3-4)
**Objective**: Implement comprehensive cost governance and automation

**Governance Components**:
1. Automated resource tagging enforcement
2. Cost anomaly detection and response
3. Budget controls with automatic actions
4. Resource lifecycle management

**Cost Governance Framework**:
```python
class CostGovernanceFramework:
    def __init__(self):
        self.organizations_client = boto3.client('organizations')
        self.budgets_client = boto3.client('budgets')
        self.ce_client = boto3.client('ce')
        self.lambda_client = boto3.client('lambda')

    def implement_tagging_governance(self):
        """Implement automated tagging governance"""

        # Service Control Policy for tagging enforcement
        tagging_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "RequireTags",
                    "Effect": "Deny",
                    "Action": [
                        "ec2:RunInstances",
                        "rds:CreateDBInstance",
                        "s3:CreateBucket"
                    ],
                    "Resource": "*",
                    "Condition": {
                        "Null": {
                            "aws:RequestedRegion": "false"
                        },
                        "ForAllValues:StringNotEquals": {
                            "aws:TagKeys": [
                                "Environment",
                                "Project",
                                "Owner",
                                "CostCenter"
                            ]
                        }
                    }
                }
            ]
        }

        # Lambda function for automated tagging
        auto_tagger_code = """
import boto3
import json

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')

    # Parse CloudTrail event
    detail = event['detail']

    if detail['eventName'] == 'RunInstances':
        instance_ids = []
        for item in detail['responseElements']['instances']:
            instance_ids.append(item['instanceId'])

        # Extract user information
        user_name = detail['userIdentity'].get('userName', 'Unknown')
        source_ip = detail['sourceIPAddress']

        # Apply default tags
        default_tags = [
            {'Key': 'AutoTagged', 'Value': 'true'},
            {'Key': 'LaunchedBy', 'Value': user_name},
            {'Key': 'LaunchTime', 'Value': detail['eventTime']},
            {'Key': 'SourceIP', 'Value': source_ip}
        ]

        # Check if required tags are missing and apply defaults
        for instance_id in instance_ids:
            try:
                ec2.create_tags(
                    Resources=[instance_id],
                    Tags=default_tags
                )
            except Exception as e:
                print(f"Error tagging instance {instance_id}: {e}")

    return {'statusCode': 200}
"""

        return {
            'tagging_policy': tagging_policy,
            'auto_tagger_function': auto_tagger_code
        }

    def setup_cost_anomaly_detection(self):
        """Set up comprehensive cost anomaly detection"""

        # Create cost anomaly detectors for different dimensions
        anomaly_detectors = []

        dimensions = [
            {'Key': 'SERVICE', 'MatchOptions': ['EQUALS']},
            {'Key': 'LINKED_ACCOUNT', 'MatchOptions': ['EQUALS']},
            {'Key': 'INSTANCE_TYPE', 'MatchOptions': ['EQUALS']}
        ]

        for dimension in dimensions:
            detector_config = {
                'AnomalyDetectorName': f"CostAnomaly-{dimension['Key']}",
                'MonitorType': 'DIMENSIONAL',
                'MonitorSpecification': {
                    'DimensionKey': dimension['Key'],
                    'MatchOptions': dimension['MatchOptions']
                }
            }

            anomaly_detectors.append(detector_config)

        # Create anomaly subscription for alerts
        subscription_config = {
            'SubscriptionName': 'CostAnomalyAlerts',
            'MonitorArnList': [],  # Will be populated with detector ARNs
            'Subscribers': [
                {
                    'Address': 'finops@company.com',
                    'Type': 'EMAIL',
                    'Status': 'CONFIRMED'
                }
            ],
            'Threshold': 100.0,  # Alert for anomalies over $100
            'Frequency': 'DAILY'
        }

        return {
            'detectors': anomaly_detectors,
            'subscription': subscription_config
        }

    def implement_budget_controls(self):
        """Implement budget controls with automatic actions"""

        # Department-level budgets with escalating actions
        budget_configs = [
            {
                'budget_name': 'Development-Monthly',
                'limit': 5000,
                'department': 'Development',
                'actions': [
                    {'threshold': 80, 'action': 'email_alert'},
                    {'threshold': 95, 'action': 'stop_non_prod_instances'},
                    {'threshold': 100, 'action': 'stop_all_instances'}
                ]
            },
            {
                'budget_name': 'Production-Monthly',
                'limit': 20000,
                'department': 'Production',
                'actions': [
                    {'threshold': 85, 'action': 'email_alert'},
                    {'threshold': 95, 'action': 'scale_down_non_critical'},
                    {'threshold': 100, 'action': 'emergency_escalation'}
                ]
            }
        ]

        # Lambda function for budget actions
        budget_action_code = """
import boto3
import json

def lambda_handler(event, context):
    # Parse budget alert
    message = json.loads(event['Records'][0]['Sns']['Message'])

    budget_name = message['BudgetName']
    actual_amount = float(message['ActualAmount'])
    forecasted_amount = float(message['ForecastedAmount'])
    threshold_type = message['ThresholdType']

    # Determine action based on budget and threshold
    if 'Development' in budget_name:
        if threshold_type == 'PERCENTAGE' and float(message['Threshold']) >= 95:
            stop_development_instances()
    elif 'Production' in budget_name:
        if threshold_type == 'PERCENTAGE' and float(message['Threshold']) >= 95:
            scale_down_non_critical_services()

    return {'statusCode': 200}

def stop_development_instances():
    ec2 = boto3.client('ec2')

    # Find development instances
    instances = ec2.describe_instances(
        Filters=[
            {'Name': 'tag:Environment', 'Values': ['dev', 'development', 'staging']},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )

    instance_ids = []
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_ids.append(instance['InstanceId'])

    if instance_ids:
        ec2.stop_instances(InstanceIds=instance_ids)

def scale_down_non_critical_services():
    autoscaling = boto3.client('autoscaling')

    # Scale down non-critical Auto Scaling Groups
    non_critical_asgs = autoscaling.describe_auto_scaling_groups(
        AutoScalingGroupNames=[
            'analytics-workers',
            'batch-processing',
            'testing-environment'
        ]
    )

    for asg in non_critical_asgs['AutoScalingGroups']:
        autoscaling.update_auto_scaling_group(
            AutoScalingGroupName=asg['AutoScalingGroupName'],
            DesiredCapacity=max(1, asg['DesiredCapacity'] // 2)
        )
"""

        return {
            'budget_configs': budget_configs,
            'action_function': budget_action_code
        }

    def implement_resource_lifecycle_management(self):
        """Implement automated resource lifecycle management"""

        lifecycle_policies = {
            'development_instances': {
                'schedule': 'Mon-Fri 9AM-6PM',
                'action': 'start_stop',
                'tags': {'Environment': 'development'}
            },
            'testing_instances': {
                'schedule': 'Business hours only',
                'action': 'start_stop',
                'tags': {'Environment': 'testing'}
            },
            'temporary_resources': {
                'max_age_days': 7,
                'action': 'terminate',
                'tags': {'Temporary': 'true'}
            },
            'unused_volumes': {
                'max_age_days': 30,
                'action': 'delete',
                'condition': 'unattached'
            }
        }

        # Lambda function for lifecycle management
        lifecycle_manager_code = """
import boto3
from datetime import datetime, timedelta

def lambda_handler(event, context):
    action = event.get('action', 'check_all')

    if action == 'stop_dev_instances':
        stop_development_instances()
    elif action == 'start_dev_instances':
        start_development_instances()
    elif action == 'cleanup_temporary':
        cleanup_temporary_resources()
    elif action == 'cleanup_volumes':
        cleanup_unused_volumes()

    return {'statusCode': 200}

def stop_development_instances():
    ec2 = boto3.client('ec2')

    # Get current time and check if it's after business hours
    current_hour = datetime.now().hour

    if current_hour >= 18 or current_hour < 9:  # After 6PM or before 9AM
        instances = ec2.describe_instances(
            Filters=[
                {'Name': 'tag:Environment', 'Values': ['development']},
                {'Name': 'instance-state-name', 'Values': ['running']}
            ]
        )

        instance_ids = []
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                instance_ids.append(instance['InstanceId'])

        if instance_ids:
            ec2.stop_instances(InstanceIds=instance_ids)

def cleanup_temporary_resources():
    ec2 = boto3.client('ec2')

    # Find instances older than 7 days with Temporary tag
    cutoff_date = datetime.now() - timedelta(days=7)

    instances = ec2.describe_instances(
        Filters=[
            {'Name': 'tag:Temporary', 'Values': ['true']}
        ]
    )

    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            launch_time = instance['LaunchTime'].replace(tzinfo=None)

            if launch_time < cutoff_date:
                print(f"Terminating temporary instance {instance['InstanceId']}")
                ec2.terminate_instances(InstanceIds=[instance['InstanceId']])

def cleanup_unused_volumes():
    ec2 = boto3.client('ec2')

    # Find unattached volumes older than 30 days
    cutoff_date = datetime.now() - timedelta(days=30)

    volumes = ec2.describe_volumes(
        Filters=[
            {'Name': 'status', 'Values': ['available']}
        ]
    )

    for volume in volumes['Volumes']:
        create_time = volume['CreateTime'].replace(tzinfo=None)

        if create_time < cutoff_date:
            print(f"Deleting unused volume {volume['VolumeId']}")
            try:
                ec2.delete_volume(VolumeId=volume['VolumeId'])
            except Exception as e:
                print(f"Error deleting volume {volume['VolumeId']}: {e}")
"""

        return {
            'policies': lifecycle_policies,
            'manager_function': lifecycle_manager_code
        }
```

## 📊 Cost Optimization Metrics

### Key Performance Indicators (KPIs)
```yaml
Financial KPIs:
  - Cost per customer/transaction
  - Month-over-month cost growth rate
  - Cost as percentage of revenue
  - Reserved Instance utilization rate
  - Spot Instance adoption percentage

Technical KPIs:
  - Resource utilization rates (CPU, memory, storage)
  - Rightsizing opportunity identification
  - Unused resource elimination rate
  - Automated cost action success rate
  - Cost anomaly detection accuracy

Operational KPIs:
  - Time to detect cost anomalies
  - Budget variance percentage
  - Cost allocation accuracy
  - Governance policy compliance rate
  - Cost optimization ROI
```

## 💰 Advanced Cost Strategies

### 1. FinOps Implementation
```python
class FinOpsFramework:
    """Implement Financial Operations best practices"""

    def __init__(self):
        self.ce_client = boto3.client('ce')
        self.organizations_client = boto3.client('organizations')

    def implement_showback_chargeback(self):
        """Implement cost allocation and chargeback"""

        # Cost allocation by business unit
        allocation_rules = {
            'cost_categories': [
                {
                    'name': 'BusinessUnit',
                    'rules': [
                        {
                            'dimension': 'LINKED_ACCOUNT',
                            'values': ['111111111111'],
                            'category': 'Engineering'
                        },
                        {
                            'dimension': 'LINKED_ACCOUNT',
                            'values': ['222222222222'],
                            'category': 'Marketing'
                        }
                    ]
                },
                {
                    'name': 'Environment',
                    'rules': [
                        {
                            'tag': 'Environment',
                            'values': ['prod', 'production'],
                            'category': 'Production'
                        },
                        {
                            'tag': 'Environment',
                            'values': ['dev', 'development'],
                            'category': 'Development'
                        }
                    ]
                }
            ]
        }

        return allocation_rules

    def create_cost_center_dashboards(self):
        """Create department-specific cost dashboards"""

        dashboard_configs = [
            {
                'department': 'Engineering',
                'metrics': [
                    'compute_costs',
                    'storage_costs',
                    'database_costs',
                    'development_environment_costs'
                ],
                'filters': {
                    'business_unit': 'Engineering',
                    'include_shared_services': True
                }
            },
            {
                'department': 'Data Science',
                'metrics': [
                    'compute_costs',
                    'ml_training_costs',
                    'data_storage_costs',
                    'analytics_costs'
                ],
                'filters': {
                    'business_unit': 'DataScience',
                    'include_gpu_instances': True
                }
            }
        ]

        return dashboard_configs
```

### 2. Green Computing and Sustainability
```python
class SustainabilityOptimizer:
    """Optimize for both cost and environmental impact"""

    def __init__(self):
        self.ec2_client = boto3.client('ec2')
        self.sustainability_client = boto3.client('sustainability')

    def optimize_for_carbon_footprint(self):
        """Optimize workloads for lower carbon footprint"""

        # Graviton instances are more energy efficient
        graviton_migration_plan = {
            't3.medium': 't4g.medium',
            't3.large': 't4g.large',
            'm5.large': 'm6g.large',
            'c5.large': 'c6g.large'
        }

        # Regions with cleaner energy sources
        green_regions = [
            'us-west-2',  # Hydroelectric
            'eu-north-1',  # Renewable energy
            'ca-central-1'  # Clean energy
        ]

        optimization_recommendations = []

        # Analyze current instances
        instances = self.ec2_client.describe_instances()

        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                current_type = instance['InstanceType']
                current_region = instance['Placement']['AvailabilityZone'][:-1]

                recommendations = {
                    'instance_id': instance['InstanceId'],
                    'current_type': current_type,
                    'current_region': current_region,
                    'actions': []
                }

                # Recommend Graviton migration
                if current_type in graviton_migration_plan:
                    recommendations['actions'].append({
                        'type': 'instance_migration',
                        'new_type': graviton_migration_plan[current_type],
                        'benefit': 'Up to 20% better performance per watt'
                    })

                # Recommend region migration
                if current_region not in green_regions:
                    recommendations['actions'].append({
                        'type': 'region_migration',
                        'recommended_regions': green_regions,
                        'benefit': 'Lower carbon footprint'
                    })

                if recommendations['actions']:
                    optimization_recommendations.append(recommendations)

        return optimization_recommendations

    def implement_workload_scheduling(self):
        """Schedule non-critical workloads during low-carbon periods"""

        # Schedule batch jobs during periods with cleaner energy
        scheduling_policy = {
            'low_carbon_hours': {
                'us-west-2': [2, 3, 4, 5, 6, 7],  # Night hours with hydro
                'eu-north-1': [10, 11, 12, 13, 14, 15],  # Day hours with solar
            },
            'workload_types': [
                'batch_processing',
                'data_analytics',
                'machine_learning_training',
                'backup_operations'
            ]
        }

        return scheduling_policy
```

## 🎯 Success Criteria

### Cost Optimization Achievements
- [ ] **Cost Reduction**: 30%+ cost reduction within 6 months
- [ ] **Utilization Improvement**: 80%+ average resource utilization
- [ ] **RI Coverage**: 70%+ Reserved Instance coverage for steady workloads
- [ ] **Spot Adoption**: 40%+ of suitable workloads on Spot Instances
- [ ] **Governance**: 95%+ compliance with tagging and budgets

### Operational Excellence
- [ ] **Automation**: 90%+ of cost optimizations automated
- [ ] **Visibility**: Real-time cost visibility across all teams
- [ ] **Response Time**: < 1 hour for cost anomaly detection
- [ ] **Culture**: FinOps practices adopted organization-wide
- [ ] **Sustainability**: 25% improvement in workload efficiency

## 🚀 Next Steps

After mastering cost optimization:
1. **Apply to [Real-world Projects](../07-real-world-projects/)** - Implement cost-optimized architectures
2. **Explore [Advanced Topics](../../07-advanced-topics/)** - Multi-region cost optimization
3. **Implement [FinOps Culture](advanced-strategies/finops.md)** - Organization-wide cost awareness

---

**Ready to optimize costs?** Start with [Cost Analysis](resource-optimization/) to identify your biggest optimization opportunities!

*Remember: Cost optimization is not a one-time activity—it's an ongoing practice that requires culture, process, and automation.*