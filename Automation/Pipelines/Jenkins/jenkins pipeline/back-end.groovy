def environment
pipeline {
     agent any
     options {
       buildDiscarder(logRotator(numToKeepStr: '50'))
       timeout(time: 10)
     }
   
   stages {

    stage('Environment Variables') {
        steps {
            script{
            if ("${params.branch}" == "develop")
            {
                env.server = "dev"
                ssmenv = "DEV"
                cpu = "256"
                memory = "512"
                source_volume = "/home/ubuntu/jenkins/jenkins_home/.dev_m2"
            }
            else if ("${params.branch}" == "release")
            {
                env.server = "stg"
                ssmenv = "STG"
                cpu = "512"
                memory = "1024"
                source_volume = "/home/ubuntu/jenkins/jenkins_home/.stg_m2"
                
            }
            else if ("${params.branch}" == "master")
            {
                env.server = "prod"
                ssmenv = "PROD"
                cpu = "512"
                memory = "1024"
                source_volume = "/home/ubuntu/jenkins/jenkins_home/.prod_m2"
                
            }
    
        }
    }
}


        
stage('checkout'){
        when {
                expression    {"${params.branch}" == "develop" || "${params.branch}" == "release" || "${params.branch}" == "master" }
            }

            steps{
                script{
                    sh "printenv | sort"
                    sh 'rm -rf * && rm -rf .git && echo "okay"'
                    checkout scm: [$class: 'GitSCM', userRemoteConfigs: [[url: "git@bitbucket.org:teamvowpay/${env.JOB_NAME}.git", ]]
                    //git branch: "${params.branch}", url: "git@bitbucket.org:teamvowpay/${env.JOB_NAME}.git"

                    }
                }
            }
        
        
stage("Create Artifact") {
        when {
                expression    {"${params.branch}" == "develop" || "${params.branch}" == "release" || "${params.branch}" == "master" }
            }
            steps{
                script{
                    
                    docker.image('maven:latest').inside("--network=jenkins_default -v ${source_volume}:/root/.m2") {
                    sh "mvn clean install -Dmaven.test.skip=true -Dfindbugs.skip=true"
                    }
                }
                    
            }
        }












stage("Creating Docker Image and Pushing to ECR") {
        when {
                expression    {"${params.branch}" == "develop" || "${params.branch}" == "release" || "${params.branch}" == "master" }
            }
                steps{
                script{
                        if (fileExists("target/${env.JOB_NAME}-0.0.1-SNAPSHOT.jar")) {
                            echo "Found"
                            withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'vowpay']]){
                                sh "eval `aws  ecr get-login --no-include-email --region eu-west-2`"
                                REPOSITORY_ID = sh(script: "aws ecr describe-repositories --region eu-west-2  --repository-names $server-${env.JOB_NAME} | jq -r '.repositories[0].repositoryUri'", returnStdout: true).trim()
                                echo "${REPOSITORY_ID}"
                                //withCredentials([string(credentialsId: "vowpaydev", variable: "vowpaydev")]) {office365ConnectorSend message: "The ${env.JOB_NAME} has been started on the branch ${params.branch}.", status: "start", color: "006666", webhookUrl: "https://outlook.office.com/webhook/0db64d18-467d-4b96-b8d0-81211eb86ed5@f6352f10-bd3b-410b-a5cd-c4e84e6b70a3/JenkinsCI/58f8522c80274c158f19844b67bac02f/9c7ca7dc-46e9-4d76-afdc-0e525143c834"}
                                withCredentials([string(credentialsId: "vowpaydev", variable: "vowpaydev")]) {office365ConnectorSend message: " ${env.JOB_NAME} service deployement has been started on the branch ${params.branch}.", status: "start", color: "006666", webhookUrl: "https://outlook.office.com/webhook/0db64d18-467d-4b96-b8d0-81211eb86ed5@f6352f10-bd3b-410b-a5cd-c4e84e6b70a3/JenkinsCI/58f8522c80274c158f19844b67bac02f/9c7ca7dc-46e9-4d76-afdc-0e525143c834"}

                                FULL_IMAGE_ID = "${REPOSITORY_ID}:latest"
                                sh "docker build  --tag ${REPOSITORY_ID}:latest ."
                                sh "docker push ${REPOSITORY_ID}:latest"
                                sh "docker image rm -f ${REPOSITORY_ID}:latest"
                                }
                            }
                         else {
                            echo "Not Found"
                            withCredentials([string(credentialsId: "vowpaydev", variable: "vowpaydev")]) {office365ConnectorSend message: "Artifact ${env.JOB_NAME}-SNAPSHOT-0.0.1.jar not found. Last commit in the branch ${params.branch}.", status: "Failure", color: "d00000", webhookUrl: "${vowpaydev}"}
                            sh "exit 1"
                            }
                        }
                    
                }
         }

        
        
        stage ("Update Task Defination and Service") {
        when {
                expression    {"${params.branch}" == "develop" || "${params.branch}" == "release" || "${params.branch}" == "master" }
            }
            steps{
                script{
                    withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'vowpay']]) {
                        sh  "cp /var/jenkins_home/sample-td-be.json sample-td.json"
                        sh "sed -e 's;%tag%;${params.tag_name};g' -e 's;%cpu%;$cpu;g' -e 's;%memory%;$memory;g' -e 's;%environment%;$server;g' -e 's;%env%;$ssmenv;g'  -e 's;%repo%;${env.JOB_NAME};g' -e 's;%account_id%;292603434312;g' sample-td.json > td.json"
                        sh "cat td.json"
                        NEW_TASK_INFO=sh(script: "aws ecs register-task-definition --region eu-west-2 --family $server-${env.JOB_NAME} --cli-input-json file://td.json", returnStdout: true)
                        TASK_REVISION= sh(script: "aws ecs describe-task-definition --region eu-west-2 --task-definition $server-${env.JOB_NAME} | jq '.taskDefinition.revision'", returnStdout: true)
                        sh (script: "aws ecs update-service --region eu-west-2 --cluster $server-vowpay --service ${env.JOB_NAME} --task-definition $server-${env.JOB_NAME}:${TASK_REVISION}", returnStdout:true)
                        sh (script: "aws ecs wait services-stable --region eu-west-2 --cluster $server-vowpay --services ${env.JOB_NAME}", returnStdout: true)
                        //sleep 20
                            
                          sh '''
                            #!/bin/sh
                            #ALB_Name="vowpay-alb"
                            if [ $branch = "develop" ]; then
                            ALB_Name="dev-vowpay-lb"
                            ALB_ARN=$(aws elbv2 describe-load-balancers --region eu-west-2 --names $ALB_Name --query 'LoadBalancers[0].LoadBalancerArn' --output text)
                            TG_ARN=$(aws elbv2 describe-target-groups  --region eu-west-2 --query "TargetGroups[?TargetGroupName=='$server-$JOB_NAME-tg'].TargetGroupArn" --output text)

                            elif  [ $branch = "release" ]; then
                            ALB_Name="stg-vowpay-lb"
                            ALB_ARN=$(aws elbv2 describe-load-balancers --region eu-west-2 --names $ALB_Name --query 'LoadBalancers[0].LoadBalancerArn' --output text)
                            TG_ARN=$(aws elbv2 describe-target-groups  --region eu-west-2 --query "TargetGroups[?TargetGroupName=='$server-$JOB_NAME-tg'].TargetGroupArn" --output text)
                            
                            else 
                            ALB_Name="prod-vowpay-lb"
                            ALB_ARN=$(aws elbv2 describe-load-balancers --region eu-west-2 --names $ALB_Name --query 'LoadBalancers[0].LoadBalancerArn' --output text)
                            TG_ARN=$(aws elbv2 describe-target-groups  --region eu-west-2 --query "TargetGroups[?TargetGroupName=='$server-$JOB_NAME-tg'].TargetGroupArn" --output text)
                            
                            
                            fi
                            STAT=$(aws elbv2 describe-target-health --region eu-west-2 --target-group-arn $TG_ARN --query 'TargetHealthDescriptions[*].TargetHealth.State' --output text)
                            
                            
                            
                            echo "$STAT"
                            while [ "$STAT" != "healthy" ]
                            do
                            STAT=$(aws elbv2 describe-target-health --region eu-west-2 --target-group-arn $TG_ARN --query 'TargetHealthDescriptions[*].TargetHealth.State' --output text)
                            #curl -X POST -H 'Content-type: application/json' --data '{"text": "'"$STAT"'" , "enviroment": "dev customer"}' https://outlook.office.com/webhook/b863e2a3-d36a-4833-991b-32fd434d8148@f6352f10-bd3b-410b-a5cd-c4e84e6b70a3/IncomingWebhook/2fe9c8c0a1c6459d963ef0310da390e4/768e38c6-c773-40c7-8e8d-49de9c561885
                            echo "--------------------------------------------------------"
                            echo  "$STAT"
                            sleep 8 
                            if [ $STAT = "healthy" ]; then
                            curl -X POST -H 'Content-type: application/json' --data '{"text": " '"$JOB_NAME"' service has been deployed sucessfully on branch '"$branch"'"}' https://outlook.office.com/webhook/0db64d18-467d-4b96-b8d0-81211eb86ed5@f6352f10-bd3b-410b-a5cd-c4e84e6b70a3/JenkinsCI/58f8522c80274c158f19844b67bac02f/9c7ca7dc-46e9-4d76-afdc-0e525143c834
                            break
                            fi
                            if [ $STAT = "unhealthy" ]; then
                            curl -X POST -H 'Content-type: application/json' --data '{"text": " '"$JOB_NAME"' service deployment has been failed on branch '"$branch"' please check the application logs"}' https://outlook.office.com/webhook/0db64d18-467d-4b96-b8d0-81211eb86ed5@f6352f10-bd3b-410b-a5cd-c4e84e6b70a3/JenkinsCI/58f8522c80274c158f19844b67bac02f/9c7ca7dc-46e9-4d76-afdc-0e525143c834
                            
                            break
                            fi
                            if [ $STAT = "draining" ]; then
                            curl -X POST -H 'Content-type: application/json' --data '{"text": " '"$JOB_NAME"' service deployment has been failed on branch '"$branch"' please check the application logs"}' https://outlook.office.com/webhook/0db64d18-467d-4b96-b8d0-81211eb86ed5@f6352f10-bd3b-410b-a5cd-c4e84e6b70a3/JenkinsCI/58f8522c80274c158f19844b67bac02f/9c7ca7dc-46e9-4d76-afdc-0e525143c834
                            
                            break
                            fi
                            done
                            #curl -X POST -H 'Content-type: application/json' --data '{"text": " job '"$JOB_NAME"'  has status  '"$STAT"'" }' https://outlook.office.com/webhook/0db64d18-467d-4b96-b8d0-81211eb86ed5@f6352f10-bd3b-410b-a5cd-c4e84e6b70a3/JenkinsCI/58f8522c80274c158f19844b67bac02f/9c7ca7dc-46e9-4d76-afdc-0e525143c834
                          
                            '''
                        }
                    }
                }
            }
    




stage("Notify") {
when {
                expression    {"${params.branch}" == "develop" || "${params.branch}" == "release" || "${params.branch}" == "master" }
            }
    steps {
               // withCredentials([string(credentialsId: "vowpaydev", variable: "vowpaydev")]) 
                //{
                    
                //office365ConnectorSend message: "*${env.JOB_NAME}* is deployed in the *$server* environment  from the *${params.branch}* branch.", status: "Success", color: "2b5329", webhookUrl: "${vowpaydev}"
                //}
                
                 echo "{$JOB_NAME}"
             }    
        }

    }
}