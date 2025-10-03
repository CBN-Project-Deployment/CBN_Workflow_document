pipeline {
    agent any

    environment {
        CBN_PASSWORD = credentials('cbn-password')
    }

    options {
        timestamps()
        ansiColor('xterm')
    }

    stages {

        stage('Checkout SCM') {
            steps {
                checkout([$class: 'GitSCM',
                          branches: [[name: '*/main']],
                          userRemoteConfigs: [[url: 'https://github.com/CBN-Project-Deployment/CBN_Workflow_document.git']]
                ])
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
                sh 'python3 -m pip install --upgrade pip --user'
                sh 'python3 -m pip install requests --user'
            }
        }

        stage('Verify Required Files') {
            steps {
                dir('CBN_Workflow_PY') {
                    script {
                        if (!fileExists('run_cbn_workflow.py')) {
                            error "❌ run_cbn_workflow.py is missing!"
                        }
                        if (!fileExists('cbn_config.py')) {
                            error "❌ cbn_config.py is missing!"
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
                        mkdir -p input_files/cpp
                        mkdir -p input_files/tdd
                        mkdir -p input_files/fdd
                        echo "✅ merged.cpp prepared" > input_files/cpp/merged.cpp
                        echo "✅ tdd input prepared" > input_files/tdd/tdd_input.txt
                        echo "✅ fdd input prepared" > input_files/fdd/fdd_input.txt
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
                                    python3 run_cbn_workflow.py cpp || true
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
                                    python3 run_cbn_workflow.py tdd || true
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
                                    python3 run_cbn_workflow.py fdd || true
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
            echo "🧹 Cleaning workspace..."
            cleanWs()
        }
        success {
            echo "✅ Pipeline succeeded"
            script {
                dir('CBN_Workflow_PY') {
                    if (fileExists('output_files')) {
                        archiveArtifacts artifacts: 'output_files/**/*', allowEmptyArchive: true
                    } else {
                        echo "⚠️ No output files to archive"
                    }
                }
            }
        }
        failure {
            echo "❌ Pipeline failed"
        }
    }
}
