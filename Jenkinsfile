pipeline {
  agent any
  stages {
    stage('Docker Test') {
      steps {
        sh 'docker ps'
      }
    }
    stage('Build Image') {
      steps {
        sh 'docker build -t smart-task-manager .'
      }
    }
  }
}

