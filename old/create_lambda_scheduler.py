#!/usr/bin/env python3
"""
Script per creare Lambda scheduler automatico per EC2
Start: 8:00 Lun-Ven
Stop: 19:00 Lun-Ven
"""
import boto3
import json
import argparse
import zipfile
import io
import time

# Regione
REGION = 'eu-west-1'

def create_iam_role():
    """Crea ruolo IAM per Lambda"""
    iam = boto3.client('iam')
    
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": ["lambda.amazonaws.com", "events.amazonaws.com"]},
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    try:
        response = iam.create_role(
            RoleName='EC2SchedulerRole',
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role per Lambda EC2 Scheduler'
        )
        role_arn = response['Role']['Arn']
        print(f"✓ Ruolo creato: {role_arn}")
    except iam.exceptions.EntityAlreadyExistsException:
        response = iam.get_role(RoleName='EC2SchedulerRole')
        role_arn = response['Role']['Arn']
        print(f"✓ Ruolo esistente: {role_arn}")
    
    # Attacca policy
    policy_arn = 'arn:aws:iam::aws:policy/AmazonEC2FullAccess'
    try:
        iam.attach_role_policy(RoleName='EC2SchedulerRole', PolicyArn=policy_arn)
        print("✓ Policy EC2 attaccata")
    except:
        pass
    
    # Policy per CloudWatch Logs
    logs_policy_arn = 'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
    try:
        iam.attach_role_policy(RoleName='EC2SchedulerRole', PolicyArn=logs_policy_arn)
        print("✓ Policy Logs attaccata")
    except:
        pass
    
    # Aspetta che il ruolo sia disponibile
    time.sleep(10)
    
    return role_arn


def create_lambda_function(function_name, instance_id, action, role_arn):
    """Crea funzione Lambda"""
    lambda_client = boto3.client('lambda', region_name=REGION)
    
    # Codice Lambda
    if action == 'start':
        lambda_code = f"""
import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2', region_name='{REGION}')
    instance_id = '{instance_id}'
    
    print(f'Starting instance {{instance_id}}...')
    ec2.start_instances(InstanceIds=[instance_id])
    
    return {{
        'statusCode': 200,
        'body': f'Started instance {{instance_id}}'
    }}
"""
    else:  # stop
        lambda_code = f"""
import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2', region_name='{REGION}')
    instance_id = '{instance_id}'
    
    print(f'Stopping instance {{instance_id}}...')
    ec2.stop_instances(InstanceIds=[instance_id])
    
    return {{
        'statusCode': 200,
        'body': f'Stopped instance {{instance_id}}'
    }}
"""
    
    # Crea ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    zip_buffer.seek(0)
    
    try:
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.11',
            Role=role_arn,
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zip_buffer.read()},
            Description=f'EC2 Scheduler - {action.upper()} instance',
            Timeout=60,
            MemorySize=128
        )
        function_arn = response['FunctionArn']
        print(f"✓ Lambda {action.upper()} creata: {function_arn}")
    except lambda_client.exceptions.ResourceConflictException:
        # Aggiorna esistente
        lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_buffer.read()
        )
        response = lambda_client.get_function(FunctionName=function_name)
        function_arn = response['Configuration']['FunctionArn']
        print(f"✓ Lambda {action.upper()} aggiornata: {function_arn}")
    
    return function_arn


def create_eventbridge_rule(rule_name, schedule, function_arn, description):
    """Crea regola EventBridge"""
    events = boto3.client('events', region_name=REGION)
    lambda_client = boto3.client('lambda', region_name=REGION)
    
    # Crea regola
    try:
        response = events.put_rule(
            Name=rule_name,
            ScheduleExpression=schedule,
            State='ENABLED',
            Description=description
        )
        rule_arn = response['RuleArn']
        print(f"✓ Regola creata: {rule_arn}")
    except Exception as e:
        print(f"✓ Regola esistente/aggiornata")
        response = events.describe_rule(Name=rule_name)
        rule_arn = response['Arn']
    
    # Aggiungi permesso Lambda
    function_name = function_arn.split(':')[-1]
    try:
        lambda_client.add_permission(
            FunctionName=function_name,
            StatementId=f'{rule_name}-Event',
            Action='lambda:InvokeFunction',
            Principal='events.amazonaws.com',
            SourceArn=rule_arn
        )
        print("✓ Permesso Lambda aggiunto")
    except lambda_client.exceptions.ResourceConflictException:
        print("✓ Permesso già esistente")
    
    # Aggiungi target
    events.put_targets(
        Rule=rule_name,
        Targets=[
            {
                'Id': '1',
                'Arn': function_arn
            }
        ]
    )
    print("✓ Target configurato")
    
    return rule_arn


def main():
    parser = argparse.ArgumentParser(description='Setup EC2 Scheduler')
    parser.add_argument('--instance-id', required=True, help='EC2 Instance ID')
    parser.add_argument('--step', required=True, choices=[
        'create-role', 'create-start-lambda', 'create-stop-lambda',
        'create-start-rule', 'create-stop-rule', 'test'
    ])
    args = parser.parse_args()
    
    instance_id = args.instance_id
    
    if args.step == 'create-role':
        create_iam_role()
    
    elif args.step == 'create-start-lambda':
        iam = boto3.client('iam')
        role = iam.get_role(RoleName='EC2SchedulerRole')
        role_arn = role['Role']['Arn']
        create_lambda_function('EC2-Start-OfficeHours', instance_id, 'start', role_arn)
    
    elif args.step == 'create-stop-lambda':
        iam = boto3.client('iam')
        role = iam.get_role(RoleName='EC2SchedulerRole')
        role_arn = role['Role']['Arn']
        create_lambda_function('EC2-Stop-OfficeHours', instance_id, 'stop', role_arn)
    
    elif args.step == 'create-start-rule':
        lambda_client = boto3.client('lambda', region_name=REGION)
        func = lambda_client.get_function(FunctionName='EC2-Start-OfficeHours')
        function_arn = func['Configuration']['FunctionArn']
        
        # Lunedì-Venerdì alle 8:00 ora italiana (7:00 UTC)
        schedule = 'cron(0 7 ? * MON-FRI *)'
        create_eventbridge_rule(
            'EC2-Start-8AM-Weekdays',
            schedule,
            function_arn,
            'Start EC2 at 8:00 AM on weekdays'
        )
    
    elif args.step == 'create-stop-rule':
        lambda_client = boto3.client('lambda', region_name=REGION)
        func = lambda_client.get_function(FunctionName='EC2-Stop-OfficeHours')
        function_arn = func['Configuration']['FunctionArn']
        
        # Lunedì-Venerdì alle 19:00 ora italiana (18:00 UTC)
        schedule = 'cron(0 18 ? * MON-FRI *)'
        create_eventbridge_rule(
            'EC2-Stop-7PM-Weekdays',
            schedule,
            function_arn,
            'Stop EC2 at 7:00 PM on weekdays'
        )
    
    elif args.step == 'test':
        print("\n✓ Setup completato!")
        print("\nVerifica:")
        print("  1. AWS Console → Lambda")
        print("     - EC2-Start-OfficeHours")
        print("     - EC2-Stop-OfficeHours")
        print("  2. AWS Console → EventBridge → Rules")
        print("     - EC2-Start-8AM-Weekdays")
        print("     - EC2-Stop-7PM-Weekdays")


if __name__ == '__main__':
    main()






















