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
                        def missingFiles = []
                        ['cbn_config.py', 'run_cbn_workflow.py'].each { f ->
                            if (!fileExists(f)) {
                                missingFiles << f
                            }
                        }
                        if (missingFiles) {
                            error "❌ Required workflow file(s) missing: ${missingFiles.join(', ')}"
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
                    touch merged.cpp

                    files=(
                        "GridCtrl.h" "GridCtrl.cpp" "CellRange.h" "GridCell.h" "GridCell.cpp"
                        "GridCellBase.h" "GridCellBase.cpp" "GridDropTarget.h" "GridDropTarget.cpp"
                        "InPlaceEdit.h" "InPlaceEdit.cpp" "MemDC.h" "TitleTip.h" "TitleTip.cpp"
                    )

                    for f in "${files[@]}"; do
                        if [ -f "../../source_code/$f" ]; then
                            cat "../../source_code/$f" >> merged.cpp
                        elif [ -f "../../source_code/GridCtrl/$f" ]; then
                            cat "../../source_code/GridCtrl/$f" >> merged.cpp
                        else
                            echo "Missing expected file: $f" >&2
                            exit 1
                        fi
                        echo -e "\\n\\n" >> merged.cpp
                    done

                    echo "✅ merged.cpp prepared"
                    '''
                }
            }
        }

        stage('Run CbN Workflow') {
            steps {
                dir('CBN_Workflow_PY') {
                    sh '''#!/bin/bash
                    set -euo pipefail
                    echo "🏃 Running CbN workflow..."
                    python3 run_cbn_workflow.py cpp
                    '''
                }
            }
        }

        stage('Archive Generated Documents') {
            steps {
                dir('CBN_Workflow_PY/output_js') {
                    archiveArtifacts artifacts: '**', fingerprint: true, allowEmptyArchive: false
                }
            }
        }

    }

    post {
        success {
            echo "✅ Pipeline succeeded."
        }
        failure {
            echo "❌ Pipeline failed! Check logs for details."
        }
        always {
            echo "🧹 Cleaning workspace..."
            cleanWs()
        }
    }
}
