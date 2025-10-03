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
                        def requiredFiles = ['run_cbn_workflow.py', 'cbn_config.py']
                        def missing = requiredFiles.findAll { !fileExists(it) }
                        if (missing) {
                            error "❌ Missing required files: ${missing.join(', ')}"
                        }
                        echo "✅ All required Python files exist"
                    }
                }
            }
        }

        stage('Prepare Input Files') {
            steps {
                dir('CBN_Workflow_PY') {
                    sh '''
                        mkdir -p input_files/cpp input_files/tdd input_files/fdd
                        echo "merged.cpp content" > input_files/cpp/merged.cpp
                        echo "tdd input" > input_files/tdd/tdd_input.txt
                        echo "fdd input" > input_files/fdd/fdd_input.txt
                    '''
                }
            }
        }

        stage('Run Workflows') {
            parallel {

                stage('Generate C++ Docs') {
                    steps {
                        dir('CBN_Workflow_PY') {
                            script {
                                echo "➡️ Running C++ workflow..."
                                def status = sh(script: 'python3 run_cbn_workflow.py cpp', returnStatus: true)
                                if (status != 0) {
                                    echo "⚠️ C++ workflow failed (exit code ${status})"
                                }
                            }
                        }
                    }
                }

                stage('Generate TDD Docs') {
                    steps {
                        dir('CBN_Workflow_PY') {
                            script {
                                echo "➡️ Running TDD workflow..."
                                def status = sh(script: 'python3 run_cbn_workflow.py tdd', returnStatus: true)
                                if (status != 0) {
                                    echo "⚠️ TDD workflow failed (exit code ${status})"
                                }
                            }
                        }
                    }
                }

                stage('Generate FDD Docs') {
                    steps {
                        dir('CBN_Workflow_PY') {
                            script {
                                echo "➡️ Running FDD workflow..."
                                def status = sh(script: 'python3 run_cbn_workflow.py fdd', returnStatus: true)
                                if (status != 0) {
                                    echo "⚠️ FDD workflow failed (exit code ${status})"
                                }
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
            dir('CBN_Workflow_PY') {
                script {
                    if (fileExists('output_files')) {
                        echo "📦 Archiving generated artifacts..."
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
