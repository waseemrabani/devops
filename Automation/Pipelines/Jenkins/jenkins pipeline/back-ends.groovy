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
                if ("${params.branch}" == "dev")
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

            }  
        }
    }
        stage('checkout'){
            when {
                    expression    {"${params.branch}" == "dev" || "${params.branch}" == "release" || "${params.branch}" == "master" }
                }

                steps{
                    script{
                        sh "printenv | sort"
                        sh 'rm -rf * && rm -rf .git && echo "okay"'
                        checkout scm: [$class: 'GitSCM', userRemoteConfigs: [[url: "git@bitbucket.org:teamvowpay/${params.repo}.git", ]], branches: [[name: "${params.branch}"]]],poll: false
                        //git branch: "${params.branch}", url: "git@bitbucket.org:teamvowpay/${env.JOB_NAME}.git"

                        }
                    }
                }
            
        
            stage("Create Artifact") {
            when {
                    expression    {"${params.branch}" == "dev" || "${params.branch}" == "release" || "${params.branch}" == "master" }
                }
                steps{
                    script{
                        GIT_COMMIT = sh (script: 'git rev-parse HEAD | cut -c1-7', returnStdout: true).trim()
                        echo "Git commit is: ${GIT_COMMIT}"
                        docker.image('maven:latest').inside("--network=jenkins_default -v ${source_volume}:/root/.m2") {
                        sh "mvn clean install -Dmaven.test.skip=true -Dfindbugs.skip=true"
                        }
                    }
                        
                }
            }

            
            

            stage("Creating Docker Image and Pushing to ECR") {
                    steps{
                    script{
                            if (fileExists("target/${params.repo}-0.0.1-SNAPSHOT.jar")) {
                                echo "Found"
                                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'vowpay']]){
                                    sh "eval `aws  ecr get-login --no-include-email --region eu-west-2`"
                                    REPOSITORY_ID = sh(script: "aws ecr describe-repositories --region eu-west-2  --repository-names $server-${params.repo} | jq -r '.repositories[0].repositoryUri'", returnStdout: true).trim()
                                    echo "${REPOSITORY_ID}"
                                    //withCredentials([string(credentialsId: "vowpaydev", variable: "vowpaydev")]) {office365ConnectorSend message: "The ${params.repo} has been started on the branch ${branch}.", status: "start", color: "006666", webhookUrl: "https://outlook.office.com/webhook/0db64d18-467d-4b96-b8d0-81211eb86ed5@f6352f10-bd3b-410b-a5cd-c4e84e6b70a3/JenkinsCI/58f8522c80274c158f19844b67bac02f/9c7ca7dc-46e9-4d76-afdc-0e525143c834"}
                                    withCredentials([string(credentialsId: "vowpaydev", variable: "vowpaydev")]) {office365ConnectorSend message: " ${params.repo} service deployement has been started on the branch ${branch}.", status: "start", color: "006666", webhookUrl: "https://outlook.office.com/webhook/0db64d18-467d-4b96-b8d0-81211eb86ed5@f6352f10-bd3b-410b-a5cd-c4e84e6b70a3/JenkinsCI/58f8522c80274c158f19844b67bac02f/9c7ca7dc-46e9-4d76-afdc-0e525143c834"}

                                    FULL_IMAGE_ID = "${REPOSITORY_ID}:latest"
                                   FULL_IMAGE_ID = "${REPOSITORY_ID}:${env.server}-${GIT_COMMIT}"
                                sh "docker build  --tag ${REPOSITORY_ID}:${env.server}-${GIT_COMMIT} ."
                                sh "docker push ${REPOSITORY_ID}:${env.server}-${GIT_COMMIT}"
                                sh "docker image rm -f ${REPOSITORY_ID}:${env.server}-${GIT_COMMIT}"
                                    }
                                }
                             else {
                                echo "Not Found"
                                withCredentials([string(credentialsId: "vowpaydev", variable: "vowpaydev")]) {office365ConnectorSend message: "Artifact ${params.repo}-SNAPSHOT-0.0.1.jar not found. Last commit in the branch ${branch}.", status: "Failure", color: "d00000", webhookUrl: "${vowpaydev}"}
                                sh "exit 1"
                                }
                            }
                        
                    }
             }

              stage ("Update Task Defination and Service") {
            steps{
                script{
                    withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'vowpay']]) {
                        sh  "cp /var/jenkins_home/sample-td-be.json sample-td.json"
                        sh "sed -e 's;%tag%;${params.tag_name};g' -e 's;%cpu%;$cpu;g' -e 's;%memory%;$memory;g' -e 's;%environment%;$server;g' -e 's;%env%;$ssmenv;g'  -e 's;%repo%;${params.repo};g' -e 's;%account_id%;292603434312;g' sample-td.json > td.json"
                        sh "cat td.json"
                        NEW_TASK_INFO=sh(script: "aws ecs register-task-definition --region eu-west-2 --family $server-${params.repo} --cli-input-json file://td.json", returnStdout: true)
                        TASK_REVISION= sh(script: "aws ecs describe-task-definition --region eu-west-2 --task-definition $server-${params.repo} | jq '.taskDefinition.revision'", returnStdout: true)
                        sh (script: "aws ecs update-service --region eu-west-2 --cluster $server-vowpay --service ${params.repo} --task-definition $server-${params.repo}:${TASK_REVISION}", returnStdout:true)
                        echo 'Waiting 5 minutes for AWS ECS to complete container replacement.'
                        sleep 30 // seconds    
                        }
                    }
                }
            }
        

    stage("Notify") {

        steps {
                    //withCredentials([string(credentialsId: "vowpaydev", variable: "vowpaydev")]) 
                    //{
                        
                    //office365ConnectorSend message: "*${params.repo}* is deployed in the *$server* environment  from the *${branch}* branch.", status: "Success", color: "2b5329", webhookUrl: "${vowpaydev}"
                    //}
                    echo "{$params.repo}"

                }    
            }

        }
    }