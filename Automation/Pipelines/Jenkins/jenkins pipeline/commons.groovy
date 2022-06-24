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
                cpu = "256"
                memory = "512"
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
                expression    {"${params.branch}" == "dev" || "${params.branch}" == "release" || "${params.branch}" == "master" }
            }

            steps{
                script{
                sh 'rm -rf * && rm -rf .git && echo "okay"'
                    git branch: "${params.branch}", url: "git@bitbucket.org:teamvowpay/${env.JOB_NAME}.git"

                    }
                }
            }
            
                      stage("Create Artifact") {
        when {
                expression    {"${params.branch}" == "dev" || "${params.branch}" == "release" || "${params.branch}" == "master" }
            }
            steps{
                script{
                    docker.image('maven:latest').inside("--network=jenkins_default -v ${source_volume}:/root/.m2") {
                    sh "mvn clean install -Dmaven.test.skip=true -Dfindbugs.skip=true"
                    }
                }
                    
            }
        }


        
        
    

stage("Notify") {
when {
                expression    {"${params.branch}" == "dev" || "${params.branch}" == "release" || "${params.branch}" == "master" }
            }
    steps {
                withCredentials([string(credentialsId: "vowpaydev", variable: "vowpaydev")]) 
                {
                    
                office365ConnectorSend message: "*${env.JOB_NAME}* is build successfully  from the *${params.branch}* branch.", status: "Success", color: "2b5329", webhookUrl: "${vowpaydev}"
                }
             }    
        }

    }
}
