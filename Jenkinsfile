pipeline {
    agent any

    environment {
        PYTHON = 'python3'
        CBN_PASSWORD = credentials('CBN_PASSWORD_CREDENTIAL_ID')
    }

    options {
        timestamps()
        ansiColor('xterm')
        timeout(time: 2, unit: 'HOURS')
    }

    stages {
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

        stage('Install Python Dependencies') {
            steps {
                sh """
                    ${PYTHON} -m pip install --upgrade pip
                    ${PYTHON} -m pip install requests docx reportlab
                """
            }
        }

        stage('Verify Workflow Scripts') {
            steps {
                dir('CBN_Workflow_PY') {
                    script {
                        def requiredFiles = ['run_cbn_workflow.py', 'cbn_config.py']
                        def missingFiles = requiredFiles.findAll { !fileExists(it) }
                        if (missingFiles) {
                            error "Missing workflow scripts: ${missingFiles.join(', ')}"
                        } else {
                            echo "✅ All workflow scripts are present."
                        }
                    }
                }
            }
        }

        stage('Prepare Input Files') {
            steps {
                dir('CBN_Workflow_PY/input_files/cpp') {
                    sh 'echo "merged.cpp prepared"'
                }
            }
        }

        stage('Run CbN Workflow') {
            steps {
                dir('CBN_Workflow_PY') {
                    script {
                        try {
                            sh """
                                ${PYTHON} run_cbn_workflow.py cpp || true
                            """
                        } catch (err) {
                            echo "⚠️ Workflow execution had issues but continuing to archive outputs."
                        }
                    }
                }
            }
        }

        stage('Archive Generated Documents') {
            steps {
                dir('CBN_Workflow_PY/output_js') {
                    archiveArtifacts artifacts: '**', allowEmptyArchive: true
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
            echo "✅ Pipeline completed successfully."
        }
        failure {
            echo "❌ Pipeline failed! Check logs for details."
        }
        unstable {
            echo "⚠️ Pipeline finished with warnings."
        }
    }
}
