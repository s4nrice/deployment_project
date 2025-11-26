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
        expression { return params.PUSH_TO_REGISTRY }
      }
      steps {
        script {
          withCredentials([usernamePassword(credentialsId: 'DOCKERHUB_CRED', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
            sh "echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin ${params.REGISTRY}"
            sh "docker push ${env.BUILT_IMAGE}"
          }
        }
      }
    }

    stage('Deploy (docker-compose)') {
      steps {
        script {
          echo 'Запускаю docker-compose (локально на агенте Jenkins).'
          sh 'docker-compose -f docker-compose.yml up -d --build'
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
