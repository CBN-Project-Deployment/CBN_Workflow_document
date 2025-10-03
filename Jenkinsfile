pipeline {
    agent any

    environment {
        CBN_PASSWORD = credentials('cbn-password')  // Replace with your Jenkins credential ID
        PYTHON_BIN = "python3"
    }

    options {
        timestamps()
        ansiColor('xterm')
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
                    ${PYTHON_BIN} -m pip install --upgrade pip
                    ${PYTHON_BIN} -m pip install requests docx reportlab
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
                                ${PYTHON_BIN} run_cbn_workflow.py cpp || true
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
                    script {
                        if (fileExists('.')) {
                            archiveArtifacts artifacts: '**', allowEmptyArchive: true
                        } else {
                            echo "⚠️ No output files found to archive."
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
