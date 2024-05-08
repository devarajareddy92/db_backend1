pipeline {
    agent any
    environment {
        VENV = '.venv'  // Assuming your virtual environment directory is named '.venv'
    }
    stages {
        stage('Checkout') {
            steps {
                checkout([$class: 'GitSCM', branches: [[name: 'main']], extensions: [], userRemoteConfigs: [[url: 'https://github.com/devarajareddy92/db_backend1.git']]])
            }
        }
        stage('Setup environment') {
            steps {
                // Activate the virtual environment
                sh "source $VENV/bin/activate"
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
