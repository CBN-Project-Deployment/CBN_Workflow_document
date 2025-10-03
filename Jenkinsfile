pipeline {
    agent any  // ensures workspace context for all steps

    environment {
        CBN_PASSWORD = credentials('cbn-password') // secure password usage
    }

    options {
        timestamps()
        ansiColor('xterm')
        timeout(time: 60, unit: 'MINUTES')
    }

    stages {

        stage('Checkout SCM') {
            steps {
                echo "🔄 Checking out main repository..."
                checkout([$class: 'GitSCM',
                          branches: [[name: '*/main']],
                          userRemoteConfigs: [[url: 'https://github.com/CBN-Project-Deployment/CBN_Workflow_document.git']]])
            }
        }

        stage('Install Dependencies') {
            steps {
                echo "📦 Installing Python dependencies..."
                sh '''
                    python3 -m pip install --upgrade pip --user
                    python3 -m pip install requests --user
                '''
            }
        }

        stage('Verify Required Files') {
            steps {
                script {
                    def requiredFiles = ['cbn_config.py', 'workflow_runner.py']
                    for (file in requiredFiles) {
                        if (!fileExists(file)) {
                            error "❌ Required file ${file} not found!"
                        }
                    }
                    echo "✅ All required files exist"
                }
            }
        }

        stage('Prepare Input Files') {
            steps {
                sh '''
                    mkdir -p input_files
                    echo "C++ input" > input_files/cpp.txt
                    echo "TDD input" > input_files/tdd.txt
                    echo "FDD input" > input_files/fdd.txt
                '''
            }
        }

        stage('Run Workflows in Parallel') {
            parallel {
                stage('C++ Workflow') {
                    steps {
                        script {
                            try {
                                sh 'python3 workflow_runner.py --type cpp --input input_files/cpp.txt'
                            } catch (err) {
                                echo "⚠️ C++ Workflow failed: ${err}"
                                currentBuild.result = 'FAILURE'
                            }
                        }
                    }
                }
                stage('TDD Workflow') {
                    steps {
                        script {
                            try {
                                sh 'python3 workflow_runner.py --type tdd --input input_files/tdd.txt'
                            } catch (err) {
                                echo "⚠️ TDD Workflow failed: ${err}"
                                currentBuild.result = 'FAILURE'
                            }
                        }
                    }
                }
                stage('FDD Workflow') {
                    steps {
                        script {
                            try {
                                sh 'python3 workflow_runner.py --type fdd --input input_files/fdd.txt'
                            } catch (err) {
                                echo "⚠️ FDD Workflow failed: ${err}"
                                currentBuild.result = 'FAILURE'
                            }
                        }
                    }
                }
            }
        }

        stage('Archive Artifacts') {
            steps {
                script {
                    // Only archive if directory exists
                    if (fileExists('output_files')) {
                        echo "📦 Archiving generated artifacts..."
                        archiveArtifacts artifacts: 'output_files/**', allowEmptyArchive: true
                    } else {
                        echo "⚠️ No artifacts to archive."
                    }
                }
            }
        }
    }

    post {
        always {
            // Wrap cleanWs in a node block to avoid MissingContextVariableException
            node {
                echo "🧹 Cleaning workspace..."
                cleanWs()
            }
        }
        success {
            echo "✅ Pipeline completed successfully!"
        }
        failure {
            echo "❌ Pipeline failed!"
        }
    }
}
