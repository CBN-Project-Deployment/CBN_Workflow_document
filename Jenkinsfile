pipeline {
    agent any

    environment {
        CBN_PASSWORD = credentials('cbn-password') // Make sure this exists in Jenkins
        PYTHON_BIN = 'python3'
    }

    options {
        timestamps()
        ansiColor('xterm')
    }

    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Checkout Repositories') {
            parallel {
                stage('CBN Workflow Code') {
                    steps {
                        dir('CBN_Workflow_PY') {
                            git url: 'https://github.com/Mrityunjai-demo/CBN_Workflow_PY.git', branch: 'main'
                        }
                    }
                }
                stage('Source App Code') {
                    steps {
                        dir('source_code') {
                            git url: 'https://github.com/ChrisMaunder/MFC-GridCtrl.git', branch: 'master'
                        }
                    }
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                sh "${PYTHON_BIN} -m pip install --upgrade pip"
                sh "${PYTHON_BIN} -m pip install requests"
            }
        }

        stage('Verify Required Files') {
            steps {
                dir('CBN_Workflow_PY') {
                    script {
                        if (!fileExists('run_cbn_workflow.py')) {
                            error "❌ Required Python file run_cbn_workflow.py is missing!"
                        }
                        echo "✅ All required .py files exist"
                    }
                }
            }
        }

        stage('Prepare Input Files') {
            steps {
                dir('CBN_Workflow_PY') {
                    sh '''
                        mkdir -p input_files/cpp input_files/tdd input_files/fdd
                        cp merged.cpp input_files/cpp/ || true
                        # Add other input preparation if needed
                        echo "✅ Input files prepared"
                    '''
                }
            }
        }

        stage('Run Workflows') {
            parallel {
                stage('Generate C++ Docs') {
                    steps {
                        dir('CBN_Workflow_PY') {
                            withCredentials([string(credentialsId: 'cbn-password', variable: 'CBN_PASSWORD')]) {
                                sh '''
                                    ${PYTHON_BIN} run_cbn_workflow.py cpp || true
                                '''
                            }
                        }
                    }
                }

                stage('Generate TDD Docs') {
                    steps {
                        dir('CBN_Workflow_PY') {
                            withCredentials([string(credentialsId: 'cbn-password', variable: 'CBN_PASSWORD')]) {
                                sh '''
                                    ${PYTHON_BIN} run_cbn_workflow.py tdd || true
                                '''
                            }
                        }
                    }
                }

                stage('Generate FDD Docs') {
                    steps {
                        dir('CBN_Workflow_PY') {
                            withCredentials([string(credentialsId: 'cbn-password', variable: 'CBN_PASSWORD')]) {
                                sh '''
                                    ${PYTHON_BIN} run_cbn_workflow.py fdd || true
                                '''
                            }
                        }
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
            node {
                echo "✅ Pipeline succeeded"
                script {
                    if (fileExists('CBN_Workflow_PY/output_files')) {
                        archiveArtifacts artifacts: 'CBN_Workflow_PY/output_files/**/*', allowEmptyArchive: true
                    }
                }
            }
        }

        failure {
            node {
                echo "❌ Pipeline failed"
            }
        }
    }
}
