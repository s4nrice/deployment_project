pipeline {
    agent any

    environment {
        IMAGE = "s4nrice/deployment_project:latest"
        VPS_HOST = "82.117.87.168"
        VPS_PATH = "/root/deploy"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build image') {
            steps {
                sh "docker build -t ${IMAGE} ."
            }
        }

        stage('Push image') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub',
                    usernameVariable: 'DOCKERHUB_USER',
                    passwordVariable: 'DOCKERHUB_PASS'
                )]) {
                    sh 'docker login -u "$DOCKERHUB_USER" -p "$DOCKERHUB_PASS"'
                    sh "docker push ${IMAGE}"
                }
            }
        }

        stage('Deploy to VPS') {
            steps {
                sshagent(['vps_ssh']) {
                    sh """
                    ssh -o StrictHostKeyChecking=no user@${VPS_HOST} '
                        cd ${VPS_PATH} &&
                        docker compose pull &&
                        docker compose up -d
                    '
                    """
                }
            }
        }
    }

    post {
        always {
            echo "Pipeline finished."
        }
    }
}
