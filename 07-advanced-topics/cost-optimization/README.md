# Cost Optimization in Distributed Systems

## Overview
Cost optimization is critical for sustainable cloud operations. This guide covers strategies, tools, and implementations for reducing infrastructure costs while maintaining performance and reliability.

## Table of Contents
1. [Cost Analysis Framework](#cost-analysis-framework)
2. [Resource Right-sizing](#resource-right-sizing)
3. [Auto-scaling Optimization](#auto-scaling-optimization)
4. [Reserved Instance Management](#reserved-instance-management)
5. [Storage Optimization](#storage-optimization)
6. [Network Cost Optimization](#network-cost-optimization)
7. [Cost Monitoring and Alerting](#cost-monitoring-and-alerting)

## Cost Analysis Framework

### Cost Tracking and Attribution

```python
import asyncio
import boto3
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from enum import Enum

class CostCategory(Enum):
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    CACHE = "cache"
    MONITORING = "monitoring"

@dataclass
class CostEntry:
    service_name: str
    category: CostCategory
    cost_amount: float
    currency: str
    time_period: datetime
    resource_id: str
    tags: Dict[str, str] = None
    usage_metrics: Dict[str, float] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = {}
        if self.usage_metrics is None:
            self.usage_metrics = {}

class CostAnalyzer:
    def __init__(self, aws_client, cost_explorer_client):
        self.aws = aws_client
        self.ce = cost_explorer_client
        self.cost_data = []

    async def collect_cost_data(self, start_date: datetime, end_date: datetime) -> List[CostEntry]:
        """Collect cost data from AWS Cost Explorer"""
        try:
            response = self.ce.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='DAILY',
                Metrics=['BlendedCost', 'UsageQuantity'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                    {'Type': 'TAG', 'Key': 'Environment'},
                    {'Type': 'TAG', 'Key': 'Team'}
                ]
            )

            cost_entries = []
            for result in response['ResultsByTime']:
                date = datetime.strptime(result['TimePeriod']['Start'], '%Y-%m-%d')

                for group in result['Groups']:
                    service = group['Keys'][0]
                    environment = group['Keys'][1] if len(group['Keys']) > 1 else 'unknown'
                    team = group['Keys'][2] if len(group['Keys']) > 2 else 'unknown'

                    cost_amount = float(group['Metrics']['BlendedCost']['Amount'])
                    usage_quantity = float(group['Metrics']['UsageQuantity']['Amount'])

                    cost_entry = CostEntry(
                        service_name=service,
                        category=self.categorize_service(service),
                        cost_amount=cost_amount,
                        currency='USD',
                        time_period=date,
                        resource_id=f"{service}-{environment}",
                        tags={'environment': environment, 'team': team},
                        usage_metrics={'quantity': usage_quantity}
                    )

                    cost_entries.append(cost_entry)

            return cost_entries

        except Exception as e:
            print(f"Error collecting cost data: {e}")
            return []

    def categorize_service(self, service_name: str) -> CostCategory:
        """Categorize AWS service into cost category"""
        service_mapping = {
            'Amazon Elastic Compute Cloud - Compute': CostCategory.COMPUTE,
            'Amazon Elastic Container Service': CostCategory.COMPUTE,
            'AWS Lambda': CostCategory.COMPUTE,
            'Amazon Simple Storage Service': CostCategory.STORAGE,
            'Amazon Elastic Block Store': CostCategory.STORAGE,
            'Amazon Relational Database Service': CostCategory.DATABASE,
            'Amazon DynamoDB': CostCategory.DATABASE,
            'Amazon ElastiCache': CostCategory.CACHE,
            'Amazon CloudWatch': CostCategory.MONITORING,
            'Amazon Route 53': CostCategory.NETWORK,
            'Amazon CloudFront': CostCategory.NETWORK,
        }

        for service_key, category in service_mapping.items():
            if service_key in service_name:
                return category

        return CostCategory.COMPUTE  # Default category

    async def analyze_cost_trends(self, cost_data: List[CostEntry], days: int = 30) -> Dict:
        """Analyze cost trends and identify anomalies"""
        df = pd.DataFrame([asdict(entry) for entry in cost_data])

        # Group by service and calculate trends
        service_trends = {}
        for service in df['service_name'].unique():
            service_data = df[df['service_name'] == service].copy()
            service_data = service_data.sort_values('time_period')

            # Calculate daily cost trend
            daily_costs = service_data.groupby('time_period')['cost_amount'].sum()

            # Calculate percentage change
            if len(daily_costs) > 1:
                pct_change = ((daily_costs.iloc[-1] - daily_costs.iloc[0]) / daily_costs.iloc[0]) * 100
                avg_daily_cost = daily_costs.mean()
                total_cost = daily_costs.sum()

                service_trends[service] = {
                    'percentage_change': pct_change,
                    'average_daily_cost': avg_daily_cost,
                    'total_cost': total_cost,
                    'trend': 'increasing' if pct_change > 10 else 'decreasing' if pct_change < -10 else 'stable'
                }

        return service_trends

    async def identify_cost_anomalies(self, cost_data: List[CostEntry], threshold: float = 2.0) -> List[Dict]:
        """Identify cost anomalies using statistical analysis"""
        df = pd.DataFrame([asdict(entry) for entry in cost_data])
        anomalies = []

        for service in df['service_name'].unique():
            service_data = df[df['service_name'] == service].copy()
            daily_costs = service_data.groupby('time_period')['cost_amount'].sum()

            # Calculate statistical thresholds
            mean_cost = daily_costs.mean()
            std_cost = daily_costs.std()
            upper_threshold = mean_cost + (threshold * std_cost)
            lower_threshold = max(0, mean_cost - (threshold * std_cost))

            # Find anomalies
            for date, cost in daily_costs.items():
                if cost > upper_threshold or cost < lower_threshold:
                    anomalies.append({
                        'service': service,
                        'date': date,
                        'cost': cost,
                        'expected_range': (lower_threshold, upper_threshold),
                        'severity': 'high' if cost > mean_cost + (3 * std_cost) else 'medium'
                    })

        return anomalies

    async def generate_cost_forecast(self, cost_data: List[CostEntry], forecast_days: int = 30) -> Dict:
        """Generate cost forecast using linear regression"""
        df = pd.DataFrame([asdict(entry) for entry in cost_data])

        forecasts = {}
        for service in df['service_name'].unique():
            service_data = df[df['service_name'] == service].copy()
            daily_costs = service_data.groupby('time_period')['cost_amount'].sum().reset_index()

            if len(daily_costs) < 7:  # Need at least a week of data
                continue

            # Prepare data for linear regression
            daily_costs['days'] = (daily_costs['time_period'] - daily_costs['time_period'].min()).dt.days
            X = daily_costs['days'].values.reshape(-1, 1)
            y = daily_costs['cost_amount'].values

            # Simple linear regression
            from sklearn.linear_model import LinearRegression
            model = LinearRegression()
            model.fit(X, y)

            # Forecast future costs
            future_days = np.arange(X[-1][0] + 1, X[-1][0] + forecast_days + 1).reshape(-1, 1)
            forecast_costs = model.predict(future_days)

            forecasts[service] = {
                'predicted_daily_costs': forecast_costs.tolist(),
                'total_forecast': float(forecast_costs.sum()),
                'confidence': model.score(X, y)  # R² score
            }

        return forecasts
```

## Resource Right-sizing

### Intelligent Resource Sizing

```python
class ResourceOptimizer:
    def __init__(self, cloudwatch_client, ec2_client):
        self.cloudwatch = cloudwatch_client
        self.ec2 = ec2_client
        self.recommendations = []

    async def analyze_ec2_utilization(self, instance_ids: List[str], days: int = 14) -> List[Dict]:
        """Analyze EC2 instance utilization and provide right-sizing recommendations"""
        recommendations = []

        for instance_id in instance_ids:
            try:
                # Get instance details
                instance_info = await self.get_instance_info(instance_id)

                # Get utilization metrics
                utilization = await self.get_instance_utilization(instance_id, days)

                # Generate recommendation
                recommendation = await self.generate_sizing_recommendation(
                    instance_info, utilization
                )

                if recommendation:
                    recommendations.append(recommendation)

            except Exception as e:
                print(f"Error analyzing instance {instance_id}: {e}")

        return recommendations

    async def get_instance_utilization(self, instance_id: str, days: int) -> Dict:
        """Get detailed utilization metrics for an instance"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)

        metrics = {}

        # CPU Utilization
        cpu_response = self.cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,  # 1 hour periods
            Statistics=['Average', 'Maximum']
        )

        cpu_values = [point['Average'] for point in cpu_response['Datapoints']]
        metrics['cpu'] = {
            'average': np.mean(cpu_values) if cpu_values else 0,
            'max': np.max(cpu_values) if cpu_values else 0,
            'p95': np.percentile(cpu_values, 95) if cpu_values else 0
        }

        # Memory Utilization (requires CloudWatch agent)
        try:
            memory_response = self.cloudwatch.get_metric_statistics(
                Namespace='CWAgent',
                MetricName='mem_used_percent',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Average', 'Maximum']
            )

            memory_values = [point['Average'] for point in memory_response['Datapoints']]
            metrics['memory'] = {
                'average': np.mean(memory_values) if memory_values else 0,
                'max': np.max(memory_values) if memory_values else 0,
                'p95': np.percentile(memory_values, 95) if memory_values else 0
            }
        except:
            metrics['memory'] = {'average': 0, 'max': 0, 'p95': 0}

        # Network utilization
        network_in = self.cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='NetworkIn',
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,
            Statistics=['Average']
        )

        network_values = [point['Average'] for point in network_in['Datapoints']]
        metrics['network'] = {
            'average_bytes': np.mean(network_values) if network_values else 0
        }

        return metrics

    async def generate_sizing_recommendation(self, instance_info: Dict, utilization: Dict) -> Optional[Dict]:
        """Generate right-sizing recommendation based on utilization"""
        current_type = instance_info['InstanceType']
        cpu_util = utilization['cpu']
        memory_util = utilization['memory']

        # Define utilization thresholds
        cpu_threshold_low = 20
        cpu_threshold_high = 80
        memory_threshold_low = 30
        memory_threshold_high = 85

        recommendation = None

        # Check if instance is over-provisioned
        if (cpu_util['p95'] < cpu_threshold_low and
            memory_util['p95'] < memory_threshold_low):

            # Recommend smaller instance
            smaller_type = await self.get_smaller_instance_type(current_type)
            if smaller_type:
                potential_savings = await self.calculate_cost_savings(
                    current_type, smaller_type
                )

                recommendation = {
                    'instance_id': instance_info['InstanceId'],
                    'current_type': current_type,
                    'recommended_type': smaller_type,
                    'reason': 'Under-utilized resources',
                    'cpu_utilization': cpu_util,
                    'memory_utilization': memory_util,
                    'potential_monthly_savings': potential_savings,
                    'confidence': 'high' if cpu_util['p95'] < 10 else 'medium'
                }

        # Check if instance is under-provisioned
        elif (cpu_util['p95'] > cpu_threshold_high or
              memory_util['p95'] > memory_threshold_high):

            # Recommend larger instance
            larger_type = await self.get_larger_instance_type(current_type)
            if larger_type:
                additional_cost = await self.calculate_cost_difference(
                    current_type, larger_type
                )

                recommendation = {
                    'instance_id': instance_info['InstanceId'],
                    'current_type': current_type,
                    'recommended_type': larger_type,
                    'reason': 'Resource constraints detected',
                    'cpu_utilization': cpu_util,
                    'memory_utilization': memory_util,
                    'additional_monthly_cost': additional_cost,
                    'confidence': 'high' if cpu_util['p95'] > 90 else 'medium'
                }

        return recommendation

    async def get_smaller_instance_type(self, current_type: str) -> Optional[str]:
        """Get appropriate smaller instance type"""
        # Simplified instance type hierarchy
        size_hierarchy = {
            't3.large': 't3.medium',
            't3.medium': 't3.small',
            't3.small': 't3.micro',
            'm5.large': 'm5.medium',
            'm5.medium': 'm5.small',
            'm5.xlarge': 'm5.large',
            'm5.2xlarge': 'm5.xlarge',
            'c5.large': 'c5.medium',
            'c5.xlarge': 'c5.large',
            'c5.2xlarge': 'c5.xlarge'
        }

        return size_hierarchy.get(current_type)

    async def calculate_cost_savings(self, current_type: str, new_type: str) -> float:
        """Calculate potential cost savings from instance type change"""
        # Simplified pricing (would use AWS Pricing API in production)
        pricing = {
            't3.micro': 8.47,
            't3.small': 16.93,
            't3.medium': 33.87,
            't3.large': 67.73,
            'm5.small': 36.50,
            'm5.medium': 73.00,
            'm5.large': 146.00,
            'm5.xlarge': 292.00,
            'm5.2xlarge': 584.00
        }

        current_cost = pricing.get(current_type, 0)
        new_cost = pricing.get(new_type, 0)

        return max(0, current_cost - new_cost)

class AutoScalingOptimizer:
    def __init__(self, autoscaling_client, cloudwatch_client):
        self.autoscaling = autoscaling_client
        self.cloudwatch = cloudwatch_client

    async def optimize_scaling_policies(self, auto_scaling_group_name: str) -> Dict:
        """Optimize auto-scaling policies based on historical patterns"""
        # Get current scaling policies
        current_policies = await self.get_current_policies(auto_scaling_group_name)

        # Analyze scaling patterns
        scaling_history = await self.get_scaling_history(auto_scaling_group_name)

        # Generate optimized policies
        optimized_policies = await self.generate_optimized_policies(
            current_policies, scaling_history
        )

        return {
            'current_policies': current_policies,
            'recommended_policies': optimized_policies,
            'potential_savings': await self.calculate_scaling_savings(
                current_policies, optimized_policies
            )
        }

    async def analyze_scaling_patterns(self, asg_name: str, days: int = 30) -> Dict:
        """Analyze auto-scaling patterns to identify optimization opportunities"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)

        # Get scaling activities
        activities = self.autoscaling.describe_scaling_activities(
            AutoScalingGroupName=asg_name,
            MaxRecords=100
        )

        # Analyze patterns
        scale_out_events = []
        scale_in_events = []

        for activity in activities['Activities']:
            if activity['StatusCode'] == 'Successful':
                if 'increase' in activity['Description'].lower():
                    scale_out_events.append(activity)
                elif 'decrease' in activity['Description'].lower():
                    scale_in_events.append(activity)

        # Calculate metrics
        avg_time_between_scales = self.calculate_avg_time_between_events(scale_out_events)
        scale_efficiency = len(scale_in_events) / max(len(scale_out_events), 1)

        return {
            'scale_out_frequency': len(scale_out_events),
            'scale_in_frequency': len(scale_in_events),
            'scale_efficiency': scale_efficiency,
            'avg_time_between_scales': avg_time_between_scales,
            'recommendations': self.generate_scaling_recommendations(
                scale_efficiency, avg_time_between_scales
            )
        }
```

## Storage Optimization

### Intelligent Storage Management

```python
class StorageOptimizer:
    def __init__(self, s3_client, ebs_client):
        self.s3 = s3_client
        self.ebs = ebs_client

    async def optimize_s3_storage(self, bucket_names: List[str]) -> List[Dict]:
        """Optimize S3 storage costs through intelligent tiering"""
        optimizations = []

        for bucket_name in bucket_names:
            try:
                # Analyze object access patterns
                access_patterns = await self.analyze_s3_access_patterns(bucket_name)

                # Generate lifecycle recommendations
                lifecycle_recommendations = await self.generate_lifecycle_rules(
                    bucket_name, access_patterns
                )

                # Calculate potential savings
                savings = await self.calculate_s3_savings(
                    bucket_name, lifecycle_recommendations
                )

                optimizations.append({
                    'bucket_name': bucket_name,
                    'access_patterns': access_patterns,
                    'recommendations': lifecycle_recommendations,
                    'potential_monthly_savings': savings
                })

            except Exception as e:
                print(f"Error optimizing bucket {bucket_name}: {e}")

        return optimizations

    async def analyze_s3_access_patterns(self, bucket_name: str) -> Dict:
        """Analyze S3 object access patterns"""
        # Get S3 analytics for the bucket
        try:
            response = self.s3.get_bucket_analytics_configuration(
                Bucket=bucket_name,
                Id='EntireBucket'
            )
        except:
            # Set up analytics if not exists
            await self.setup_s3_analytics(bucket_name)
            return {'status': 'analytics_setup_pending'}

        # Simulate access pattern analysis (would use CloudTrail logs in production)
        objects_info = await self.get_bucket_objects_info(bucket_name)

        patterns = {
            'total_objects': len(objects_info),
            'total_size_gb': sum(obj['size'] for obj in objects_info) / (1024**3),
            'objects_by_age': self.categorize_objects_by_age(objects_info),
            'access_frequency': await self.estimate_access_frequency(bucket_name)
        }

        return patterns

    async def generate_lifecycle_rules(self, bucket_name: str, access_patterns: Dict) -> List[Dict]:
        """Generate intelligent lifecycle rules"""
        rules = []

        # Rule 1: Transition frequently accessed files to IA after 30 days
        if access_patterns.get('access_frequency', {}).get('frequent', 0) > 0:
            rules.append({
                'rule_name': 'frequent_to_ia',
                'transition': {
                    'days': 30,
                    'storage_class': 'STANDARD_IA'
                },
                'filter': 'all_objects',
                'estimated_savings_percent': 40
            })

        # Rule 2: Transition infrequently accessed files to Glacier after 90 days
        rules.append({
            'rule_name': 'infrequent_to_glacier',
            'transition': {
                'days': 90,
                'storage_class': 'GLACIER'
            },
            'filter': 'all_objects',
            'estimated_savings_percent': 65
        })

        # Rule 3: Archive very old files to Deep Archive after 365 days
        rules.append({
            'rule_name': 'old_to_deep_archive',
            'transition': {
                'days': 365,
                'storage_class': 'DEEP_ARCHIVE'
            },
            'filter': 'all_objects',
            'estimated_savings_percent': 85
        })

        return rules

    async def optimize_ebs_volumes(self, volume_ids: List[str]) -> List[Dict]:
        """Optimize EBS volumes for cost and performance"""
        optimizations = []

        for volume_id in volume_ids:
            try:
                # Get volume info
                volume_info = await self.get_volume_info(volume_id)

                # Get utilization metrics
                utilization = await self.get_volume_utilization(volume_id)

                # Generate optimization recommendation
                recommendation = await self.generate_ebs_recommendation(
                    volume_info, utilization
                )

                if recommendation:
                    optimizations.append(recommendation)

            except Exception as e:
                print(f"Error optimizing volume {volume_id}: {e}")

        return optimizations

    async def get_volume_utilization(self, volume_id: str, days: int = 14) -> Dict:
        """Get EBS volume utilization metrics"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)

        # Get IOPS utilization
        read_ops = self.cloudwatch.get_metric_statistics(
            Namespace='AWS/EBS',
            MetricName='VolumeReadOps',
            Dimensions=[{'Name': 'VolumeId', 'Value': volume_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,
            Statistics=['Average', 'Maximum']
        )

        write_ops = self.cloudwatch.get_metric_statistics(
            Namespace='AWS/EBS',
            MetricName='VolumeWriteOps',
            Dimensions=[{'Name': 'VolumeId', 'Value': volume_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,
            Statistics=['Average', 'Maximum']
        )

        read_values = [point['Average'] for point in read_ops['Datapoints']]
        write_values = [point['Average'] for point in write_ops['Datapoints']]

        total_iops = [(r + w) for r, w in zip(read_values, write_values)]

        return {
            'average_iops': np.mean(total_iops) if total_iops else 0,
            'peak_iops': np.max(total_iops) if total_iops else 0,
            'iops_utilization_percent': (np.mean(total_iops) / 3000) * 100 if total_iops else 0  # Assuming gp2
        }

    async def generate_ebs_recommendation(self, volume_info: Dict, utilization: Dict) -> Optional[Dict]:
        """Generate EBS optimization recommendation"""
        current_type = volume_info['VolumeType']
        current_size = volume_info['Size']
        current_iops = volume_info.get('Iops', 0)

        avg_iops = utilization['average_iops']
        peak_iops = utilization['peak_iops']

        recommendation = None

        # Check for over-provisioned IOPS
        if current_type == 'io1' and peak_iops < (current_iops * 0.3):
            # Recommend switching to gp2
            potential_savings = await self.calculate_ebs_savings(
                current_type, 'gp2', current_size, current_iops
            )

            recommendation = {
                'volume_id': volume_info['VolumeId'],
                'current_type': current_type,
                'recommended_type': 'gp2',
                'reason': 'IOPS over-provisioned',
                'current_iops': current_iops,
                'actual_usage': avg_iops,
                'potential_monthly_savings': potential_savings
            }

        # Check for gp2 that could benefit from gp3
        elif current_type == 'gp2' and current_size > 100:
            # gp3 is often more cost-effective for larger volumes
            potential_savings = await self.calculate_gp2_to_gp3_savings(current_size)

            recommendation = {
                'volume_id': volume_info['VolumeId'],
                'current_type': 'gp2',
                'recommended_type': 'gp3',
                'reason': 'gp3 more cost-effective for this size',
                'current_size': current_size,
                'potential_monthly_savings': potential_savings
            }

        return recommendation
```

This comprehensive cost optimization guide provides practical tools and strategies for reducing cloud infrastructure costs while maintaining system performance and reliability. The implementations cover resource analysis, intelligent right-sizing, auto-scaling optimization, and storage cost management.