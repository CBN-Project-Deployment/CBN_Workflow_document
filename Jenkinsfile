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
                        def missing = []
                        ['cbn_config.py', 'run_cbn_workflow.py'].each { f ->
                            if (!fileExists(f)) { missing << f }
                        }
                        if (missing) {
                            error "❌ Required file(s) missing: ${missing.join(', ')}"
                        } else {
                            echo "✅ All workflow scripts are present."
                        }
                    }
                }
            }
        }

        stage('Prepare Input Files') {
            steps {
                dir('CBN_Workflow_PY') {
                    sh '''#!/bin/bash
                        set -euo pipefail
                        mkdir -p input_files/cpp
                        touch input_files/cpp/merged.cpp

                        files=(
                          "GridCtrl.h" "GridCtrl.cpp" "CellRange.h"
                          "GridCell.h" "GridCell.cpp" "GridCellBase.h" "GridCellBase.cpp"
                          "GridDropTarget.h" "GridDropTarget.cpp"
                          "InPlaceEdit.h" "InPlaceEdit.cpp"
                          "MemDC.h" "TitleTip.h" "TitleTip.cpp"
                        )

                        for f in "${files[@]}"; do
                          if [ -f "../source_code/$f" ]; then
                            cat "../source_code/$f" >> input_files/cpp/merged.cpp
                          elif [ -f "../source_code/GridCtrl/$f" ]; then
                            cat "../source_code/GridCtrl/$f" >> input_files/cpp/merged.cpp
                          else
                            echo "❌ Missing expected file: $f" >&2
                            exit 1
                          fi
                          echo -e "\\n\\n" >> input_files/cpp/merged.cpp
                        done

                        echo "✅ merged.cpp prepared in CBN_Workflow_PY/input_files/cpp"
                    '''
                }
            }
        }

        stage('Run CbN Workflow') {
            steps {
                dir('CBN_Workflow_PY') {
                    sh '''
                        python3 run_cbn_workflow.py cpp
                    '''
                }
            }
        }

        stage('Archive Generated Documents') {
            steps {
                archiveArtifacts artifacts: 'CBN_Workflow_PY/output_js/**', fingerprint: true, onlyIfSuccessful: true
                archiveArtifacts artifacts: 'generated_docs/**', fingerprint: true, onlyIfSuccessful: true
            }
        }

    }

    post {
        success {
            echo "✅ Pipeline succeeded."
        }
        always {
            echo "🧹 Cleaning workspace..."
            cleanWs()
        }
        failure {
            echo "❌ Pipeline failed! Check logs for details."
        }
    }
}
