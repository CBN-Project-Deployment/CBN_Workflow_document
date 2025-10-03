pipeline {
    agent any

    environment {
        // Securely inject password into environment
        CBN_PASSWORD = credentials('cbn_password')
    }

    options {
        ansiColor('xterm')
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
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
                            git url: 'https://github.com/Mrityunjai-demo/CBN_Workflow_PY.git', branch: 'main'
                        }
                    }
                }
                stage('Source Application Code') {
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
                        if (!fileExists('run_cbn_workflow.py') || !fileExists('cbn_config.py')) {
                            error "❌ Missing workflow scripts!"
                        }
                        echo "✅ All workflow scripts are present."
                    }
                }
            }
        }

        stage('Prepare Input Files') {
            steps {
                dir('CBN_Workflow_PY') {
                    sh '''
                        mkdir -p input_files/cpp
                        # Merge or copy .cpp files from source_code
                        if ls ../source_code/*.cpp >/dev/null 2>&1; then
                            cat ../source_code/*.cpp > input_files/cpp/merged.cpp
                            echo "✅ merged.cpp created from source_code"
                        else
                            echo "⚠️ No .cpp files found in source_code, using placeholder."
                            echo "// empty merged.cpp" > input_files/cpp/merged.cpp
                        fi
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
                    archiveArtifacts artifacts: 'CBN_Workflow_PY/output_js/**, CBN_Workflow_PY/output_docs/**', allowEmptyArchive: true
                }
            }
        }
    }

    post {
        always {
            echo "🧹 Cleaning workspace..."
            cleanWs()
        }
        failure {
            echo "❌ Pipeline failed. Check logs for details."
        }
        success {
            echo "✅ Pipeline finished successfully!"
        }
    }
}
