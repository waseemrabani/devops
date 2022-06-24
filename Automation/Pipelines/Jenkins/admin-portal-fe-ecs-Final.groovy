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
            if ("${params.branch}" == "xplora-admin-portal")
            {
                env.server = "dev2"
                ssmenv = "DEV"
                cpu = "256"
                memory = "512"
                //source_volume = "/home/ubuntu/jenkins/jenkins_home/.dev_m2"
            }
            else if ("${params.branch}" == "release")
            {
                env.server = "stg"
                ssmenv = "STG"
                cpu = "256"
                memory = "512"
                //source_volume = "/home/ubuntu/jenkins/jenkins_home/.stg_m2"
                
            }
            else if ("${params.branch}" == "master")
            {
                env.server = "prod"
                ssmenv = "PROD"
                cpu = "512"
                memory = "1024"
                //source_volume = "/home/ubuntu/jenkins/jenkins_home/.prod_m2"
                
            }
    
        }
    }
}

        
       stage('checkout'){
        when {
                expression    {"${params.branch}" == "xplora-admin-portal" || "${params.branch}" == "release" || "${params.branch}" == "master" }
            }

            steps{
                script{
                    sh "printenv | sort"
                    sh 'rm -rf * && rm -rf .git && echo "okay"'
                    git branch: "${params.branch}", url: "git@bitbucket.org:teamvowpay/${env.JOB_NAME}.git"
                    sh "pwd"
                    }
                }
            }
        
        
        stage("Create Artifact") {
        when {
                expression    {"${params.branch}" == "xplora-admin-portal" || "${params.branch}" == "release" || "${params.branch}" == "master" }
            }
            steps{
                script{
                    
                    docker.image('admin-portal-fe:latest').inside("--network=jenkins_default") {
                    //docker.image('admin-portal-fe:latest').inside("--network=jenkins_default -v ${source_volume}:/root/.m2") {
                    sh "ls -altr"
                    sh "node -v"
                    sh "npm i"
                    sh "npm install http-server"
                    //sh  "npm run build"
                    //sh "ls -altr"
                    sh '''
                    npm run build
                    if [ $? -eq 0 ]
                    then
                    echo "SUCCESS"
                    
                    #curl -X POST -H 'Content-type: application/json' --data '{"text": " '"$JOB_NAME"' npm build seccuss '"$branch"'"}' https://outlook.office.com/webhook/0db64d18-467d-4b96-b8d0-81211eb86ed5@f6352f10-bd3b-410b-a5cd-c4e84e6b70a3/JenkinsCI/58f8522c80274c158f19844b67bac02f/9c7ca7dc-46e9-4d76-afdc-0e525143c834
                    else
                    
                    echo "FAIL"
                    
                    #curl -X POST -H 'Content-type: application/json' --data '{"text": " '"$JOB_NAME"' npm build fails '"$branch"' please check the application logs"}' https://outlook.office.com/webhook/0db64d18-467d-4b96-b8d0-81211eb86ed5@f6352f10-bd3b-410b-a5cd-c4e84e6b70a3/JenkinsCI/58f8522c80274c158f19844b67bac02f/9c7ca7dc-46e9-4d76-afdc-0e525143c834

                    fi
                    
                    '''
                    

                    

                    }
                }
                    
            }
        }
        
        

        stage("Creating Docker Image and Pushing to ECR") {
        when {
                expression    {"${params.branch}" == "xplora-admin-portal" || "${params.branch}" == "release" || "${params.branch}" == "master" }
            }
                steps{
                script{
                        if (fileExists("package.json")) {
                            echo "Found"
                            withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'xpay']]){
                                sh "aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin 409947039396.dkr.ecr.eu-west-1.amazonaws.com/dev2-admin-portal-fe"
                                REPOSITORY_ID = sh(script: "aws ecr describe-repositories --region eu-west-1 --repository-names $server-${env.JOB_NAME} | jq -r '.repositories[0].repositoryUri'", returnStdout: true).trim()
                                echo "${REPOSITORY_ID}"
                                // withCredentials([string(credentialsId: "xpay", variable: "xpay")]) {office365ConnectorSend message: " ${env.JOB_NAME} service deployement has been started on the branch ${params.branch}.", status: "start", color: "006666", webhookUrl: "https://outlook.office.com/webhook/0db64d18-467d-4b96-b8d0-81211eb86ed5@f6352f10-bd3b-410b-a5cd-c4e84e6b70a3/JenkinsCI/58f8522c80274c158f19844b67bac02f/9c7ca7dc-46e9-4d76-afdc-0e525143c834"}
                                FULL_IMAGE_ID = "${REPOSITORY_ID}:latest"
                                sh "docker build  --tag ${REPOSITORY_ID}:latest ."
                                // sh "`aws  ecr get-login-password  --region eu-west-1  | docker login --username AWS --password-stdin 409947039396.dkr.ecr.eu-west-1.amazonaws.com`"
                                sh "docker push ${REPOSITORY_ID}:latest"
                                sh "docker image rm -f ${REPOSITORY_ID}:latest"
                                }
                            }
                         else {
                            echo "Not Found"
                            withCredentials([string(credentialsId: "xpay", variable: "xpay")]) {office365ConnectorSend message: "Artifact ${env.JOB_NAME}-SNAPSHOT-0.0.1.jar not found. Last commit in the branch ${params.branch}.", status: "Failure", color: "d00000", webhookUrl: "${xpay}"}
                            sh "exit 1"
                            }
                        }
                    
                }
         }

        stage ("Update Task Defination and Service") {
        when {
                expression    {"${params.branch}" == "xplora-admin-portal" || "${params.branch}" == "release" || "${params.branch}" == "master" }
            }
            steps{
                script{
                    withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'xpay']]) {
                        sh  "cp /var/jenkins_home/sample-td-be-admin.json sample-td.json"
                        sh "sed -e 's;%tag%;${params.tag_name};g' -e 's;%cpu%;$cpu;g' -e 's;%memory%;$memory;g' -e 's;%environment%;$server;g' -e 's;%env%;$ssmenv;g'  -e 's;%repo%;${env.JOB_NAME};g' -e 's;%account_id%;292603434312;g' sample-td.json > td.json"
                        sh "cat td.json"
                        NEW_TASK_INFO=sh(script: "aws ecs register-task-definition --region eu-west-1 --family $server-${env.JOB_NAME} --cli-input-json file://td.json", returnStdout: true)
                        TASK_REVISION= sh(script: "aws ecs describe-task-definition --region eu-west-1 --task-definition ${env.JOB_NAME} | jq '.taskDefinition.revision'", returnStdout: true)
                        sh (script: "aws ecs update-service --region eu-west-1 --cluster $server-xplora  --service ${env.JOB_NAME} --task-definition ${env.JOB_NAME}:${TASK_REVISION}", returnStdout:true)
                        //sleep 160
                        sh (script: "aws ecs wait services-stable --region eu-west-1 --cluster $server-xplora --services ${env.JOB_NAME}", returnStdout: true)

                            sh '''   
                            ALB_Name="dev-goplay-lb"
                            ALB_ARN=$(aws elbv2 describe-load-balancers --region eu-west-1 --names $ALB_Name --query 'LoadBalancers[0].LoadBalancerArn' --output text)
                            TG_ARN=$(aws elbv2 describe-target-groups  --region eu-west-1 --query "TargetGroups[?TargetGroupName=='$JOB_NAME-tg'].TargetGroupArn" --output text)

                            
                            STAT=$(aws elbv2 describe-target-health --region eu-west-1 --target-group-arn $TG_ARN --query 'TargetHealthDescriptions[*].TargetHealth.State' --output text)
                            
                            
                            echo "$STAT"
                            while [ "$STAT" != "healthy" ]
                            do
                            STAT=$(aws elbv2 describe-target-health --region eu-west-1 --target-group-arn $TG_ARN --query 'TargetHealthDescriptions[*].TargetHealth.State' --output text)
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
                expression    {"${params.branch}" == "xplora-admin-portal" || "${params.branch}" == "release" || "${params.branch}" == "master" }
            }
    steps {
               //withCredentials([string(credentialsId: "xpay", variable: "xpay")]) 
                //{
                    
                //office365ConnectorSend message: "*${env.JOB_NAME}* is deployed in the *$server* environment  from the *${params.branch}* branch.", status: "Success", color: "2b5329", webhookUrl: "${xpay}"
                //}
                                echo "{$JOB_NAME}"

             }    
        }

    }
}