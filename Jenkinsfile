pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                checkout([$class: 'GitSCM', branches: [[name: 'main']], extensions: [], userRemoteConfigs: [[url: 'https://github.com/devarajareddy92/pytest-intro-vs-M.git']]])
            }
        }
        stage('Setup environment') {
            steps {
                // Install any necessary system packages
                sh 'sudo apt-get update && sudo apt-get install -y python3-venv python3-pip'
                // Optionally, create and activate a virtual environment
                sh 'python3 -m venv venv && source venv/bin/activate'
            }
        }
        stage('Install dependencies') {
            steps {
                // Install Python dependencies using pip
                sh 'pip install -r requirements.txt'
            }
        }
        stage('Build') {
            steps {
                // Perform any additional build steps
                sh 'python app.py build' // Example: Running a setup.py file for building
            }
        }
    }
    post {
        success {
            // Actions to perform when the pipeline succeeds
            echo 'Pipeline succeeded!'
        }
        failure {
            // Actions to perform when the pipeline fails
            echo 'Pipeline failed!'
        }
    }
}
