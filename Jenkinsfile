pipeline {
    agent any
    environment {
        VENV = '.venv'  // Assuming your virtual environment directory is named '.venv'
        DEPLOY_DIR = '/Devar/db'
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
                script {
                    // Modify PATH to include virtual environment's bin directory
                    withEnv(["PATH+=$VENV/bin"]) {
                        sh 'pip install --upgrade pip setuptools'
                    }
                }
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
                script {
                    // Redirect output to a log file and show the last few lines to diagnose long running issues
                    sh 'python3 app.py > build_log.txt 2>&1 &'
                    // Monitor the output for a while to ensure it starts correctly
                    sleep 30
                    sh 'tail -n 100 build_log.txt'
                }
            }
        }
       stage('Deploy') {
            steps {
                // Copy the Python files to the deployment directory
                sh "cp -r * ${DEPLOY_DIR}"
                // Navigate to the deployment directory
                dir("${DEPLOY_DIR}") {
                    // Start the Python application
                    sh "nohup python3 app.py &"
                }
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
