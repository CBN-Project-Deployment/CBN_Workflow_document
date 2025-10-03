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
        OUTPUT_DIR = "generated_docs"
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
                            error "❌ Required workflow file(s) missing: ${missing.join(', ')}"
                        } else {
                            echo "✅ All workflow scripts are present."
                        }
                    }
                }
            }
        }

        stage('Prepare Input Files') {
            steps {
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
                    if [ -f "source_code/$f" ]; then
                      cat "source_code/$f" >> input_files/cpp/merged.cpp
                    elif [ -f "source_code/GridCtrl/$f" ]; then
                      cat "source_code/GridCtrl/$f" >> input_files/cpp/merged.cpp
                    else
                      echo "❌ Missing expected file: $f" >&2
                      exit 1
                    fi
                    echo -e "\\n\\n" >> input_files/cpp/merged.cpp
                  done

                  echo "✅ merged.cpp prepared"
                '''
            }
        }

        stage('Run CbN Workflow') {
            steps {
                dir('CBN_Workflow_PY') {
                    sh """
                      mkdir -p ../${OUTPUT_DIR}
                      ${PYTHON} run_cbn_workflow.py cpp --input ../input_files/cpp/merged.cpp --output ../${OUTPUT_DIR}
                    """
                }
            }
        }

        stage('Archive Generated Documents') {
            steps {
                archiveArtifacts artifacts: "${OUTPUT_DIR}/*", fingerprint: true
            }
        }
    }

    post {
        success {
            echo "✅ Pipeline completed successfully. Documents generated."
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
