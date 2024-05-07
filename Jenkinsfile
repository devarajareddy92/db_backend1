pipeline {
    agent any
 
    stages {
        stage('Checkout') {
            steps {
                git 'http://10.101.104.22:8090/cloudytech/db_backend.git'
            }
        }
        stage('Setup environment') {
            steps {
                sh 'sudo apt-get update && sudo apt-get install -y python3-pip'
                sh 'python3 -m venv venv && source venv/bin/activate'
            }
        }
        stage('Install dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }
        stage('Build') {
            steps {
                sh 'python setup.py build'
            }
        }

 
    post {
        success {
            echo 'Pipeline succeeded!'
            // Add any post-success actions here
        }
        failure {
            echo 'Pipeline failed!'
            // Add any post-failure actions here
        }
    }
}
