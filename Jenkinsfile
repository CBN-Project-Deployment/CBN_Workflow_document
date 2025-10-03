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
                    python3 -m pip install --upgrade pip
                    python3 -m pip install requests
                '''
            }
        }

        stage('Verify Required Files') {
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
                            echo "✅ All required .py files exist"
                        }
                    }
                }
            }
        }

        stage('Prepare Input Files') {
            steps {
                sh '''
                set -euo pipefail

                # Create input directories
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
                            withCredentials([string(credentialsId: 'CBN_PASSWORD_CREDENTIAL_ID', variable: 'CBN_PASSWORD')]) {
                                sh '''
                                    if [ -n "$(ls input_files/cpp 2>/dev/null)" ]; then
                                        python3 run_cbn_workflow.py cpp || true
                                    else
                                        echo "⚠ No C++ input files found, skipping..."
                                    fi
                                '''
                            }
                        }
                    }
                }

                stage('Generate TDD Docs') {
                    steps {
                        dir('CBN_Workflow_PY') {
                            withCredentials([string(credentialsId: 'CBN_PASSWORD_CREDENTIAL_ID', variable: 'CBN_PASSWORD')]) {
                                sh '''
                                    if [ -n "$(ls input_files/tdd 2>/dev/null)" ]; then
                                        python3 run_cbn_workflow.py tdd || true
                                    else
                                        echo "⚠ No TDD input files found, skipping..."
                                    fi
                                '''
                            }
                        }
                    }
                }

                stage('Generate FDD Docs') {
                    steps {
                        dir('CBN_Workflow_PY') {
                            withCredentials([string(credentialsId: 'CBN_PASSWORD_CREDENTIAL_ID', variable: 'CBN_PASSWORD')]) {
                                sh '''
                                    if [ -n "$(ls input_files/fdd 2>/dev/null)" ]; then
                                        python3 run_cbn_workflow.py fdd || true
                                    else
                                        echo "⚠ No FDD input files found, skipping..."
                                    fi
                                '''
                            }
                        }
                    }
                }
            }
        }
    }

    post {
        success {
            echo "✅ Pipeline succeeded."
            script {
                if (fileExists('CBN_Workflow_PY/output_files')) {
                    archiveArtifacts artifacts: 'CBN_Workflow_PY/output_files/**/*.js', fingerprint: true
                } else {
                    echo "⚠ No output files to archive"
                }
            }
        }

        always {
            echo "🧹 Cleaning workspace..."
            cleanWs()
        }

        failure {
            echo "❌ Pipeline failed!"
        }
    }
}
