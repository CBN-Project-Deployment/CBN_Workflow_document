pipeline {
    agent any

    options {
        timestamps()
        ansiColor('xterm')
        disableConcurrentBuilds()
    }

    environment {
        PYTHON = 'python3'
        CBN_PASSWORD = credentials('CBN_PASSWORD_CREDENTIAL_ID')
        WORKSPACE_DIR = "${env.WORKSPACE}"
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
                        def missing = []
                        ['cbn_config.py', 'run_cbn_workflow.py'].each { f ->
                            if (!fileExists(f)) { missing << f }
                        }
                        if (missing) {
                            error "❌ Required workflow script(s) missing: ${missing.join(', ')}"
                        } else {
                            echo "✅ All required workflow scripts exist."
                        }
                    }
                }
            }
        }

        stage('Prepare Input Files') {
            steps {
                dir('CBN_Workflow_PY/input_files/cpp') {
                    sh '''#!/bin/bash
                        set -euo pipefail
                        mkdir -p .
                        > merged.cpp

                        SOURCE_DIR="${WORKSPACE_DIR}/source_code"

                        files=(
                            "GridCtrl.h" "GridCtrl.cpp" "CellRange.h" "GridCell.h" "GridCell.cpp"
                            "GridCellBase.h" "GridCellBase.cpp" "GridDropTarget.h" "GridDropTarget.cpp"
                            "InPlaceEdit.h" "InPlaceEdit.cpp" "MemDC.h" "TitleTip.h" "TitleTip.cpp"
                        )

                        for f in "${files[@]}"; do
                            file_path=$(find "$SOURCE_DIR" -name "$f" | head -n 1)
                            if [ -f "$file_path" ]; then
                                cat "$file_path" >> merged.cpp
                                echo -e "\\n\\n" >> merged.cpp
                            else
                                echo "⚠️ Warning: Expected file not found: $f — skipping"
                            fi
                        done

                        echo "✅ merged.cpp prepared"
                    '''
                }
            }
        }

        stage('Run CbN Workflow') {
            steps {
                dir('CBN_Workflow_PY') {
                    sh 'python3 run_cbn_workflow.py cpp || true'
                }
            }
        }

        stage('Archive Generated Documents') {
            steps {
                dir('CBN_Workflow_PY/output_js') {
                    archiveArtifacts artifacts: '**/*', fingerprint: true, allowEmptyArchive: true
                }
            }
        }
    }

    post {
        success {
            echo "✅ Pipeline completed successfully."
        }
        failure {
            echo "❌ Pipeline failed. Check logs for details."
        }
        always {
            echo "🧹 Cleaning workspace..."
            cleanWs()
        }
    }
}
