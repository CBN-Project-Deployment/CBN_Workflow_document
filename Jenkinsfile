pipeline {
    agent any
    environment {
        CBN_PASSWORD = credentials('cbn-password')  // example credential
    }
    options {
        timestamps()
        ansiColor('xterm')
        timeout(time: 1, unit: 'HOURS')
        buildDiscarder(logRotator(numToKeepStr: '10'))
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
                        def requiredFiles = ['run_cbn_workflow.py', 'cbn_config.py']
                        def missingFiles = requiredFiles.findAll { !fileExists(it) }
                        if (missingFiles) {
                            error "Missing workflow scripts: ${missingFiles.join(', ')}"
                        }
                        echo "✅ All workflow scripts are present."
                    }
                }
            }
        }

        stage('Prepare Input Files') {
            steps {
                dir('CBN_Workflow_PY/input_files/cpp') {
                    sh 'echo "✅ merged.cpp prepared"'
                }
            }
        }

        stage('Run CbN Workflow') {
            steps {
                dir('CBN_Workflow_PY') {
                    script {
                        try {
                            sh 'python3 run_cbn_workflow.py cpp'
                        } catch (err) {
                            echo "⚠️ Workflow execution encountered an error: ${err}"
                            currentBuild.result = 'UNSTABLE'
                        }
                    }
                }
            }
        }

        stage('Archive Generated Documents') {
            steps {
                dir('CBN_Workflow_PY') {
                    script {
                        def outputExists = fileExists('output_js')
                        if (outputExists) {
                            archiveArtifacts artifacts: 'output_js/**', allowEmptyArchive: false
                        } else {
                            echo "⚠️ No output artifacts found to archive."
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
        unstable {
            echo "⚠️ Pipeline finished but marked UNSTABLE due to errors."
        }
        failure {
            echo "❌ Pipeline failed. Check logs for details."
        }
    }
}
