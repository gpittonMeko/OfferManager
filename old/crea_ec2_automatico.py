#!/usr/bin/env python3
"""
Script per creare istanza EC2 automaticamente
"""
import boto3
import time
import sys

def crea_istanza_ec2():
    """Crea istanza EC2 per OfferManager"""
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     CREAZIONE AUTOMATICA ISTANZA EC2 PER OFFERMANAGER       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Inizializza client EC2
        ec2 = boto3.client('ec2', region_name='eu-west-1')  # Irlanda
        
        print("✓ Connesso ad AWS")
        print("\n[1/5] Creazione Security Group...")
        
        # Crea Security Group
        try:
            sg = ec2.create_security_group(
                GroupName='OfferManager-SG',
                Description='Security group per OfferManager CRM'
            )
            sg_id = sg['GroupId']
            
            # Aggiungi regole
            ec2.authorize_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 22,
                        'ToPort': 22,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    },
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 80,
                        'ToPort': 80,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    },
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 5000,
                        'ToPort': 5000,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    }
                ]
            )
            print(f"✓ Security Group creato: {sg_id}")
            
        except ec2.exceptions.ClientError as e:
            if 'already exists' in str(e):
                # Usa esistente
                response = ec2.describe_security_groups(GroupNames=['OfferManager-SG'])
                sg_id = response['SecurityGroups'][0]['GroupId']
                print(f"✓ Security Group esistente: {sg_id}")
            else:
                raise
        
        print("\n[2/5] Creazione istanza EC2...")
        
        # Crea istanza (CONFIGURAZIONE ECONOMICA - Free Tier)
        instances = ec2.run_instances(
            ImageId='ami-0905a3c97561e0b69',  # Ubuntu 22.04 LTS eu-west-1
            InstanceType='t2.micro',  # FREE TIER eligible!
            KeyName='LLM_14',
            SecurityGroupIds=[sg_id],
            MinCount=1,
            MaxCount=1,
            BlockDeviceMappings=[
                {
                    'DeviceName': '/dev/sda1',
                    'Ebs': {
                        'VolumeSize': 8,  # 8GB minimo (Free Tier = 30GB gratis)
                        'VolumeType': 'gp3',  # più economico di gp2
                        'DeleteOnTermination': True
                    }
                }
            ],
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {'Key': 'Name', 'Value': 'OfferManager-CRM'},
                        {'Key': 'Project', 'Value': 'OfferManager'},
                        {'Key': 'CostCenter', 'Value': 'FreeTier'}
                    ]
                }
            ]
        )
        
        instance_id = instances['Instances'][0]['InstanceId']
        print(f"✓ Istanza creata: {instance_id}")
        
        print("\n[3/5] Attesa avvio istanza...")
        print("(Può richiedere 1-2 minuti)")
        
        # Aspetta che sia running
        waiter = ec2.get_waiter('instance_running')
        waiter.wait(InstanceIds=[instance_id])
        
        print("✓ Istanza avviata!")
        
        print("\n[4/5] Recupero IP pubblico...")
        
        response = ec2.describe_instances(InstanceIds=[instance_id])
        ip_pubblico = response['Reservations'][0]['Instances'][0]['PublicIpAddress']
        
        print(f"✓ IP Pubblico: {ip_pubblico}")
        
        print("\n[5/5] Attesa inizializzazione sistema...")
        print("(30 secondi per boot completo)")
        time.sleep(30)
        
        print("\n" + "="*60)
        print("  ✅ ISTANZA EC2 CREATA CON SUCCESSO!")
        print("="*60)
        print(f"\n📍 IP Pubblico: {ip_pubblico}")
        print(f"🔑 Instance ID: {instance_id}")
        print(f"💰 Tipo: t2.micro (FREE TIER - Gratis anno 1!)")
        print(f"💾 Storage: 8 GB gp3")
        print(f"\n📋 Prossimi passi:")
        print(f"  1. Esegui: 🚀 DEPLOY SU AWS ECONOMICO.bat")
        print(f"  2. Scegli opzione 1")
        print(f"  3. Inserisci IP: {ip_pubblico}")
        print(f"  4. Aspetta 5 minuti")
        print(f"  5. Accedi: http://{ip_pubblico}")
        print(f"\n💡 RISPARMIO:")
        print(f"  • Quando NON usi, STOPPA istanza = 0€/giorno")
        print(f"  • Usa: GESTISCI_EC2_COSTI.bat")
        print("\n" + "="*60)
        
        # Salva info
        with open('ec2_info.txt', 'w') as f:
            f.write(f"IP Pubblico: {ip_pubblico}\n")
            f.write(f"Instance ID: {instance_id}\n")
            f.write(f"Security Group: {sg_id}\n")
            f.write(f"Region: eu-west-1\n")
            f.write(f"Data creazione: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print("\n✓ Info salvate in: ec2_info.txt")
        
        return ip_pubblico
        
    except Exception as e:
        print(f"\n❌ Errore: {str(e)}")
        print("\nPossibili cause:")
        print("  1. AWS CLI non configurato")
        print("  2. Credenziali mancanti/errate")
        print("  3. Key pair 'LLM_14' non esiste nella regione")
        print("  4. Limite istanze raggiunto")
        print("\nSoluzione:")
        print("  Segui SETUP_AWS_MANUALE.txt per creare manualmente")
        return None


if __name__ == '__main__':
    ip = crea_istanza_ec2()
    
    if ip:
        print(f"\n\nPer continuare:")
        print(f"  Doppio click: DEPLOY_AUTOMATICO.bat")
        print(f"  Inserisci IP: {ip}")
        input("\nPremi INVIO per uscire...")

