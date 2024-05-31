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
                script {
                    // Create and activate the virtual environment
                    sh 'python3 -m venv ${VENV}'
                    withEnv(["PATH=${VENV}/bin:$PATH"]) {
                        sh 'pip install --upgrade pip setuptools'
                    }
                }
            }
        }
        stage('Install dependencies') {
            steps {
                script {
                    // Activate the virtual environment and install dependencies
                    withEnv(["PATH=${VENV}/bin:$PATH"]) {
                        sh 'pip install -r requirements.txt'
                    }
                }
            }
        }
        stage('Build') {
            steps {
                script {
                    // Activate the virtual environment and start the app
                    withEnv(["PATH=${VENV}/bin:$PATH"]) {
                        sh 'python app.py > build_log.txt 2>&1 &'
                        sleep 30
                        sh 'tail -n 100 build_log.txt'
                    }
                }
            }
        }
        stage('Deploy') {
            steps {
                script {
                    // Ensure the deployment directory is writable
                    sh "sudo chown -R ${env.USER}:${env.USER} ${DEPLOY_DIR}"
                    
                    // Copy files to the deployment directory
                    sh "cp -r * ${DEPLOY_DIR}"
                    
                    // Navigate to the deployment directory and start the app
                    dir("${DEPLOY_DIR}") {
                        withEnv(["PATH=${VENV}/bin:$PATH"]) {
                            sh "nohup python app.py &"
                        }
                    }
                }
            }
        }
    }
    post {
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
