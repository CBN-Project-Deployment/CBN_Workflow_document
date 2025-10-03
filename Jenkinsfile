pipeline {
    agent any

    environment {
        CBN_PASSWORD = credentials('cbn-password') // Jenkins credential ID
        PYTHON_BIN = 'python3'
    }

    options {
        timestamps()
        ansiColor('xterm')
    }

    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm
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
                sh '''
                    ${PYTHON_BIN} -m pip install --upgrade pip
                    ${PYTHON_BIN} -m pip install requests
                '''
            }
        }

        stage('Verify Required Files') {
            steps {
                script {
                    if (!fileExists('CBN_Workflow_PY/run_cbn_workflow.py')) {
                        error "❌ Missing run_cbn_workflow.py"
                    }
                    echo "✅ All required .py files exist"
                }
            }
        }

        stage('Prepare Input Files') {
            steps {
                sh '''
                    #!/bin/bash
                    set -euo pipefail

                    mkdir -p CBN_Workflow_PY/input_files/cpp
                    mkdir -p CBN_Workflow_PY/input_files/tdd
                    mkdir -p CBN_Workflow_PY/input_files/fdd

                    # Merge C++ files
                    touch CBN_Workflow_PY/input_files/cpp/merged.cpp
                    files=(GridCtrl.h GridCtrl.cpp CellRange.h GridCell.h GridCell.cpp GridCellBase.h GridCellBase.cpp GridDropTarget.h GridDropTarget.cpp InPlaceEdit.h InPlaceEdit.cpp MemDC.h TitleTip.h TitleTip.cpp)
                    for f in "${files[@]}"; do
                        if [ -f "source_code/$f" ]; then
                            cat "source_code/$f" >> CBN_Workflow_PY/input_files/cpp/merged.cpp
                        elif [ -f "source_code/GridCtrl/$f" ]; then
                            cat "source_code/GridCtrl/$f" >> CBN_Workflow_PY/input_files/cpp/merged.cpp
                        else
                            echo "⚠ Missing expected file: $f" >&2
                        fi
                        echo -e "\n\n" >> CBN_Workflow_PY/input_files/cpp/merged.cpp
                    done
                    echo "✅ merged.cpp prepared in CBN_Workflow_PY/input_files/cpp/"

                    # Copy TDD/FDD templates if they exist
                    if [ -d "CBN_Workflow_PY/templates/tdd" ]; then
                        cp CBN_Workflow_PY/templates/tdd/* CBN_Workflow_PY/input_files/tdd/ || true
                    fi
                    if [ -d "CBN_Workflow_PY/templates/fdd" ]; then
                        cp CBN_Workflow_PY/templates/fdd/* CBN_Workflow_PY/input_files/fdd/ || true
                    fi
                '''
            }
        }

        stage('Run Workflows') {
            parallel {
                stage('Generate C++ Docs') {
                    steps {
                        dir('CBN_Workflow_PY') {
                            withCredentials([string(credentialsId: 'cbn-password', variable: 'CBN_PASSWORD')]) {
                                sh '''
                                    set +e
                                    ${PYTHON_BIN} run_cbn_workflow.py cpp || true
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
                                    set +e
                                    ${PYTHON_BIN} run_cbn_workflow.py tdd || true
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
                                    set +e
                                    ${PYTHON_BIN} run_cbn_workflow.py fdd || true
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
            // Only archive if output files exist
            script {
                def outputExists = fileExists('CBN_Workflow_PY/output_files')
                if (outputExists) {
                    archiveArtifacts artifacts: 'CBN_Workflow_PY/output_files/**/*', allowEmptyArchive: true
                }
            }
        }
        failure {
            echo "❌ Pipeline failed"
        }
    }
}
