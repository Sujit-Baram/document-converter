pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    environment {
        AWS_REGION = 'us-east-2'
        AWS_ACCOUNT_ID = '533267015112'
        ECR_REPOSITORY = 'document-converter/dev'
        IMAGE_TAG = "${BUILD_NUMBER}"
        ECR_REGISTRY = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        IMAGE_URI = "${ECR_REGISTRY}/${ECR_REPOSITORY}:${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements-dev.txt
                    pytest -q
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build --pull -t "${IMAGE_URI}" .
                    docker image inspect "${IMAGE_URI}" >/dev/null
                '''
            }
        }

        stage('Authenticate to ECR') {
            steps {
                // Prefer an EC2 instance profile / IAM role on the Jenkins agent.
                sh '''
                    aws sts get-caller-identity
                    aws ecr get-login-password --region "${AWS_REGION}" |
                      docker login --username AWS --password-stdin "${ECR_REGISTRY}"
                '''
            }
        }

        stage('Push Image to ECR') {
            steps {
                sh '''
                    docker push "${IMAGE_URI}"
                    docker tag "${IMAGE_URI}" "${ECR_REGISTRY}/${ECR_REPOSITORY}:latest"
                    docker push "${ECR_REGISTRY}/${ECR_REPOSITORY}:latest"
                '''
            }
        }

        stage('Deployment Handoff') {
            steps {
                echo "Image pushed: ${IMAGE_URI}"
                echo "Update app_image in environments/dev/terraform.tfvars to this exact URI."
                echo "Then run terraform plan, review it, and apply the reviewed plan."
                echo "Your launch template embeds the image URI in User Data, so ASG instances must refresh."
            }
        }
    }

    post {
        always {
            sh 'docker logout "${ECR_REGISTRY}" || true'
            sh 'docker image prune -f || true'
        }
        success {
            echo "Build and ECR push completed. Check Deployment Handoff for the image URI."
        }
        failure {
            echo "Pipeline failed. Review the stage logs before retrying."
        }
    }
}
