pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
    }

    environment {
        // Comment out if you don’t actually need credentials
        // CBN_PASSWORD = credentials('cbn_password')
    }

    stages {

        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Checkout Repositories') {
            parallel {
                stage('CbN Workflow Repo') {
                    steps {
                        dir('CBN_Workflow_PY') {
                            git branch: 'main', url: 'https://github.com/Mrityunjai-demo/CBN_Workflow_PY.git'
                        }
                    }
                }
                stage('Source Application Code') {
                    steps {
                        dir('source_code') {
                            git branch: 'master', url: 'https://github.com/ChrisMaunder/MFC-GridCtrl.git'
                        }
                    }
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m pip install --upgrade pip
                    python3 -m pip install requests docx reportlab
                '''
            }
        }

        stage('Verify Workflow Scripts') {
            steps {
                dir('CBN_Workflow_PY') {
                    script {
                        if (fileExists('run_cbn_workflow.py')) {
                            echo "✅ All workflow scripts are present."
                        } else {
                            error "❌ Missing run_cbn_workflow.py"
                        }
                    }
                }
            }
        }

        stage('Prepare Input Files') {
            steps {
                dir('CBN_Workflow_PY') {
                    sh '''
                        mkdir -p input_files/cpp
                        cp ../source_code/merged.cpp input_files/cpp/ || true
                        echo "✅ merged.cpp prepared in CBN_Workflow_PY/input_files/cpp"
                    '''
                }
            }
        }

        stage('Run CbN Workflow') {
            steps {
                dir('CBN_Workflow_PY') {
                    retry(2) {
                        timeout(time: 10, unit: 'MINUTES') {
                            sh 'python3 run_cbn_workflow.py cpp'
                        }
                    }
                }
            }
        }

        stage('Archive Generated Documents') {
            steps {
                script {
                    if (fileExists('CBN_Workflow_PY/generated_docs')) {
                        archiveArtifacts artifacts: 'CBN_Workflow_PY/generated_docs/**', fingerprint: true
                    } else {
                        echo "⚠️ No generated documents found to archive."
                    }
                }
            }
        }
    }

    post {
        always {
            node {
                echo "🧹 Cleaning workspace..."
                cleanWs()
            }
        }
        success {
            echo "✅ Pipeline completed successfully."
        }
        failure {
            echo "❌ Pipeline failed. Check logs for details."
        }
    }
}
