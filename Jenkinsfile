pipeline {
    agent any

    environment {
        // adjust these paths to match your Jenkins node
        PYTHON_HOME = "C:\\Python39"            // optional: if you have a system python
        VENV_DIR    = "${WORKSPACE}\\.venv"
        PERSISTENT_DIR = "D:\\persistent_models" // where to persist model artifacts on the agent
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Prepare Python (Windows)') {
            steps {
                // Create venv and install deps
                bat '''
                @echo off
                if not exist "%VENV_DIR%\\Scripts\\python.exe" (
                  python -m venv "%VENV_DIR%"
                )
                call "%VENV_DIR%\\Scripts\\activate"
                python -m pip install --upgrade pip
                pip install -r requirements.txt || pip install scikit-learn joblib
                '''
            }
        }

        stage('Train model') {
            steps {
                // run training script
                bat '''
                @echo off
                call "%VENV_DIR%\\Scripts\\activate"
                python train.py
                '''
            }
        }

        stage('Archive artifact') {
            steps {
                // tell Jenkins to archive the model file so it shows in build artifacts
                archiveArtifacts artifacts: 'src/model/**', fingerprint: true
            }
        }

        stage('Persist locally (robocopy)') {
            steps {
                bat '''
                @echo off
                echo ==== COPY TO PERSISTENT DIR (robocopy) ====
                echo Copying entire workspace to %PERSISTENT_DIR%
                REM Ensure destination exists
                powershell -NoProfile -Command "New-Item -ItemType Directory -Force -Path '%PERSISTENT_DIR%'"
                REM /MIR mirrors the directory (be careful: deletes at dest if removed from src)
                REM /NFL /NDL minimize log lines; /R:2 /W:2 quick retry settings
                robocopy "%WORKSPACE%" "%PERSISTENT_DIR%\\%JOB_NAME%_%BUILD_NUMBER%" /E /Z /MT:8 /R:2 /W:2 /NFL /NDL
                echo Robocopy exit code: %ERRORLEVEL%
                '''
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: '**/test-results/*.xml' // optional
            cleanWs()
        }
    }
}
