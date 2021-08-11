from aws_cdk import (
        core as cdk,
        aws_sns as sns,
        aws_ec2 as ec2,
        aws_iam as iam,
        aws_s3 as s3,
        aws_s3_deployment as deploy
)

class AwSappStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        #S3 bucket for script
        script_bucket=s3.Bucket(self, "scriptbucket", bucket_name="botscripts2231", public_read_access=True)

        deploy.BucketDeployment(self, "DeployScripts",
                sources=[deploy.Source.asset("./scripts")],
                destination_bucket=script_bucket
        )

        #Setup VPC, endpoint for SNS, create public subnet
        vpc = ec2.Vpc(self, "VPC",
            cidr="10.0.0.0/16",
            nat_gateways=0,
            subnet_configuration=[ec2.SubnetConfiguration(name="public",subnet_type=ec2.SubnetType.PUBLIC)]
            )
        
        #Add security group to allow SSH to ec2
        my_security_group = ec2.SecurityGroup(self, "SecurityGroup",
            vpc=vpc,
            description="Allow ssh access to ec2 instances",
            allow_all_outbound=True
        )
        
        my_security_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "allow ssh access from the world")
               
        vpc.add_interface_endpoint("SNSenpoint",  service=ec2.InterfaceVpcEndpointAwsService.SNS)
        
        #Create ec2 with Amazon AMI, IAM role for s3 and security group.
        ami = ec2.MachineImage.latest_amazon_linux(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2)

        role = iam.Role(self, "Role",
          assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))

        role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            resources=["*"],
            actions=["s3:GetObject", "s3:ListBucket", "cloudformation:DescribeStacks"]
        ))

        instance = ec2.Instance(self, "Instance",
            role=role,
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ami,
            vpc = vpc,
            security_group = my_security_group
            )

        #User data to download script from s3. Should be run manually and check the cronjob is correctly set up.
        instance.user_data.add_commands(
            "cd /home/ec2-user",
            "aws s3api get-object --bucket botscripts2231 --key userdata userdata.sh 2>>log.txt ",
            "chmod 700 userdata"
            )
        
        #Setup SNS topic. Subscriptions need to be manually added.
        topic = sns.Topic(self, "TestTopic",
                display_name = "Tests available"
                )

        #Cloudformation output for s3 bucket name
        cdk.CfnOutput(self, "bucketName",
                value=script_bucket.bucket_name,
                export_name="scriptbucket"
                )

