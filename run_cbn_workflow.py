pipeline {
    agent any

    options {
        timestamps()
        ansiColor('xterm')
        disableConcurrentBuilds()
    }

    environment {
        PYTHON = 'python3'
        CBN_PASSWORD = credentials('CBN_PASSWORD_CREDENTIAL_ID') // Jenkins credential
        OUTPUT_DIR = "generated_output"
        REACT_REPO = "git@github.com:Mrityunjai-demo/React-Dep.git"
        REACT_BRANCH = "main"
    }

    stages {

        stage('Checkout C++ Source Code') {
            steps {
                dir('source_code') {
                    git branch: 'master', url: 'https://github.com/ChrisMaunder/MFC-GridCtrl.git'
                }
            }
        }

        stage('Checkout CbN Workflow Repo') {
            steps {
                dir('CBN_Workflow_PY') {
                    git branch: 'main', url: 'https://github.com/CBN-Project-Deployment/CBN_Workflow_document.git'
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
                    "MemDC.h"
                    "TitleTip.h" "TitleTip.cpp"
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

        stage('Run CbN Workflow - Generate Documents') {
            steps {
                dir('CBN_Workflow_PY') {
                    sh """
                      mkdir -p ../${OUTPUT_DIR}/docs
                      ${PYTHON} run_cbn_workflow.py tdd --output ../${OUTPUT_DIR}/docs/TDD.docx
                      ${PYTHON} run_cbn_workflow.py fdd --output ../${OUTPUT_DIR}/docs/FDD.docx
                    """
                }
            }
        }

        stage('Run CbN Workflow - Generate React Code') {
            steps {
                dir('CBN_Workflow_PY') {
                    sh """
                      mkdir -p ../${OUTPUT_DIR}/react
                      ${PYTHON} run_cbn_workflow.py cpp_to_react \
                        --input ../input_files/cpp/merged.cpp \
                        --output ../${OUTPUT_DIR}/react
                    """
                }
            }
        }

        stage('Push Generated React Code to Git') {
            steps {
                dir("${OUTPUT_DIR}/react") {
                    sh '''
                      git init
                      git remote add origin ${REACT_REPO}
                      git checkout -B ${REACT_BRANCH}
                      git add .
                      git -c user.name="jenkins-bot" -c user.email="jenkins@ci.local" commit -m "Auto-generated React code from CbN workflow [ci skip]" || echo "No changes to commit"
                      git push origin ${REACT_BRANCH} --force
                    '''
                }
            }
        }

        stage('Archive Generated Documents') {
            steps {
                archiveArtifacts artifacts: "${OUTPUT_DIR}/docs/*.docx", fingerprint: true
            }
        }
    }

    post {
        success {
            echo "✅ Pipeline completed successfully. Documents + ReactJS code generated."
        }
        failure {
            echo "❌ Pipeline failed. Check logs for errors."
        }
        always {
            echo "🧹 Cleaning workspace..."
            cleanWs()
        }
    }
}
