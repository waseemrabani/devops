def environment
pipeline {
     agent any
     options {
       buildDiscarder(logRotator(numToKeepStr: '50'))
       timeout(time: 10)
     }
   
   stages {

//     stage('Environment Variables') {
//         steps {
//             script{
//             if ("${params.branch}" == "master")
//             {
//                 env.server = "dev"
//                 ssmenv = "DEV"
//                 cpu = "256"
//                 memory = "512"
//                 //source_volume = "/home/ubuntu/jenkins/jenkins_home/.dev_m2"
//             }
//             else if ("${params.branch}" == "release")
//             {
//                 env.server = "stg"
//                 ssmenv = "STG"
//                 cpu = "256"
//                 memory = "512"
//                 //source_volume = "/home/ubuntu/jenkins/jenkins_home/.stg_m2"
                
//             }
    
//         }
//     }
//  }      
       stage('Get Code'){
        when {
                expression    {"${params.branch}" == "develop" || "${params.branch}" == "master" || "${params.branch}" == "release" }
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
                expression    {"${params.branch}" == "develop" || "${params.branch}" == "master" || "${params.branch}" == "release" }
            }
            steps{
                script{
                    sh "ls -ahl"
                    sh "pwd"
                    // Building Java Code to Create a JAR using Docker's Maven Image
                    docker.image('node:14.15.5-alpine3.13').inside("--network=isolated_network -w /app -v /var/jenkins_home/workspace/website@tmp/durable-b82bf8fb/script.sh") {
                    sh "ls -altr"
                    sh "npm i"
                    //sh "npm install http-server"
                    sh "npm run build"
                    //sh "rm -rf build"
                    sh '''
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
        
        stage('Deploying on dev'){
        when {
                expression    { "${params.branch}" == "develop" }
            }

            steps{
                script{
                    sh "pwd"
                    sh "ls -altr"
                    sh "cd build"
                    sh "ls -altr"
                    sh "aws s3 rm s3://dev.vowpay.com  --recursive"
                    sh "aws s3 cp build s3://dev.vowpay.com  --recursive"
                    //sh "aws cloudfront create-invalidation --distribution-id E2MPWOQVHTXHO3 --paths '/*'"
                    }
                }
            }

        stage('Deploying on stage'){
        when {
                expression    { "${params.branch}" == "release" }
            }

            steps{
                script{
                    sh "pwd"
                    sh "ls -altr"
                    sh "cd build"
                    sh "ls -altr"
                    sh "aws s3 rm s3://www.stg.vowpay.com  --recursive"
                    sh "aws s3 cp build s3://www.stg.vowpay.com  --recursive"
                    sh "aws cloudfront create-invalidation --distribution-id E2MPWOQVHTXHO3 --paths '/*'"
                    }
                }
            }

        stage('Deploying on Prod'){
        when {
                expression    {"${params.branch}" == "master"  }
            }

            steps{
                script{
                    sh "pwd"
                    sh "ls -altr"
                    sh "aws s3 rm s3://prod.vowpay.com  --recursive"
                    sh "aws s3 cp build s3://prod.vowpay.com  --recursive"
                    sh "aws cloudfront create-invalidation --distribution-id E3NNKLODEZZQIW --paths '/*'"
                    }
                }
            }    
stage("Notify") {
when {
                expression    {"${params.branch}" == "develop" || "${params.branch}" == "master" || "${params.branch}" == "release" }
            }
    steps {
               //withCredentials([string(credentialsId: "vowpaydev", variable: "vowpaydev")]) 
                //{
                    
                //office365ConnectorSend message: "*${env.JOB_NAME}* is deployed in the *$server* environment  from the *${params.branch}* branch.", status: "Success", color: "2b5329", webhookUrl: "${vowpaydev}"
                //}
                                echo "{$JOB_NAME}"

             }    
        }

    }
}