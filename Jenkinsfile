pipeline {
  agent any

  parameters {
    string(name: 'IMAGE_NAME', defaultValue: 'deployment_project', description: 'Имя образа (без реестра)')
    string(name: 'REGISTRY', defaultValue: '', description: 'Реестр Docker (пример: docker.io/youruser) — оставьте пустым для локальной сборки')
    booleanParam(name: 'PUSH_TO_REGISTRY', defaultValue: false, description: 'Пушить ли собранный образ в реестр')
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build image') {
      steps {
        script {
          def gitShort = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
          def imageTag = "${params.IMAGE_NAME}:${gitShort}"
          def fullImage = params.REGISTRY?.trim() ? "${params.REGISTRY}/${imageTag}" : imageTag
          echo "Building image ${fullImage}"
          sh "docker build -t ${fullImage} ."
          env.BUILT_IMAGE = fullImage
        }
      }
    }

    stage('Push image') {
      when {
        expression { return params.PUSH_TO_REGISTRY && params.REGISTRY?.trim() }
      }
      steps {
        script {
          withCredentials([usernamePassword(credentialsId: 'DOCKERHUB_CRED', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
            sh 'docker login -u "$DOCKER_USER" -p "$DOCKER_PASS" "$REGISTRY"'
            sh "docker push ${env.BUILT_IMAGE}"
            echo "Image pushed to registry: ${env.BUILT_IMAGE}"
          }
        }
      }
    }

    stage('Deploy (docker-compose) - Local') {
      when {
        expression { return !params.PUSH_TO_REGISTRY }
      }
      steps {
        script {
          echo 'Локальный деплой через docker-compose (без пуша в реестр).'
          sh 'docker-compose -f docker-compose.yml up -d --build'
        }
      }
    }

    stage('Deploy to VPS') {
      when {
        expression { return params.PUSH_TO_REGISTRY && params.REGISTRY?.trim() }
      }
      steps {
        script {
          echo "Деплой на VPS: пулим образ ${env.BUILT_IMAGE} и перезапускаем docker-compose."
          withCredentials([sshUserPrivateKey(credentialsId: 'VPS_SSH', keyFileVariable: 'SSH_KEY', usernameVariable: 'SSH_USER')]) {
            def vpsHost = env.VPS_HOST ?: 'your-vps-ip-or-domain'
            def vpsPath = env.VPS_DEPLOY_PATH ?: '/opt/deployment_project'
            
            sh """
              ssh -o StrictHostKeyChecking=no -i ${SSH_KEY} ${SSH_USER}@${vpsHost} << 'EOF'
                cd ${vpsPath}
                docker-compose pull
                docker-compose up -d
                docker-compose ps
EOF
            """
          }
        }
      }
    }
  }

  post {
    always {
      echo 'Pipeline finished.'
    }
  }
}
