// Jenkinsfile - Cross-platform Python pipeline with diagnostics
pipeline {
  agent any

  environment {
    VENV = 'venv'
    REPORT_DIR = 'reports'
    DIST_DIR = 'dist'
  }

  options {
    buildDiscarder(logRotator(daysToKeepStr: '14'))
    timestamps()
    disableConcurrentBuilds()
  }

  stages {

    stage('Checkout') {
      steps {
        echo "Checking out repository..."
        checkout scm
      }
    }

    stage('Agent diagnostics') {
      steps {
        script {
          if (isUnix()) {
            sh '''
              echo "=== Unix diagnostics ==="
              uname -a || true
              echo "PATH=$PATH"
              command -v python3 || command -v python || echo "python not found"
              python3 --version 2>/dev/null || python --version 2>/dev/null || true
            '''
          } else {
            bat '''
              @echo off
              echo === Windows diagnostics ===
              echo COMPUTERNAME=%COMPUTERNAME%
              echo PATH=%PATH%
              where py || where python || echo "python/py not found"
              py --version 2>nul || python --version 2>nul || echo "no python version available"
            '''
          }
        }
      }
    }

    stage('Create venv & upgrade pip') {
      steps {
        script {
          if (isUnix()) {
            sh '''
              set -e
              # choose python3 or python
              if command -v python3 >/dev/null 2>&1; then
                PY=python3
              elif command -v python >/dev/null 2>&1; then
                PY=python
              else
                echo "ERROR: python not found on PATH. Install Python on this agent."
                exit 1
              fi
              echo "Using $PY to create venv"
              $PY -m venv ${VENV}
              ${VENV}/bin/python -m pip install --upgrade pip setuptools wheel
            '''
          } else {
            // Windows: prefer py -3, fall back to python
            bat '''
            @echo off
            setlocal enabledelayedexpansion
            set PY_CMD=
            where py >nul 2>&1
            if %ERRORLEVEL%==0 ( set PY_CMD=py -3 ) else (
              where python >nul 2>&1
              if %ERRORLEVEL%==0 ( set PY_CMD=python ) else (
                echo ERROR: Neither 'py' nor 'python' found on PATH. Install Python on this agent and restart Jenkins.
                exit /b 1
              )
            )
            echo Using %PY_CMD% to create venv
            %PY_CMD% -m venv %VENV%
            "%VENV%\\Scripts\\python.exe" -m pip install --upgrade pip setuptools wheel
            endlocal
            '''
          }
        }
      }
    }

    stage('Install dependencies') {
      steps {
        script {
          if (isUnix()) {
            sh '''
              set -e
              if [ -f requirements.txt ]; then
                ${VENV}/bin/python -m pip install -r requirements.txt
              else
                echo "No requirements.txt found; skipping pip install"
              fi
            '''
          } else {
            bat '''
            @echo off
            if exist requirements.txt (
              "%VENV%\\Scripts\\python.exe" -m pip install -r requirements.txt
            ) else (
              echo No requirements.txt found; skipping pip install
            )
            '''
          }
        }
      }
    }

    stage('Run tests (pytest)') {
      steps {
        script {
          if (isUnix()) {
            sh '''
              set -e
              mkdir -p ${REPORT_DIR}
              ${VENV}/bin/python -m pip install -U pytest || true
              ${VENV}/bin/python -m pytest --junitxml=${REPORT_DIR}/results.xml || true
            '''
          } else {
            bat '''
            @echo off
            if not exist %REPORT_DIR% mkdir %REPORT_DIR%
            "%VENV%\\Scripts\\python.exe" -m pip install -U pytest || exit /b 0
            "%VENV%\\Scripts\\python.exe" -m pytest --junitxml=%REPORT_DIR%\\results.xml || exit /b 0
            '''
          }
        }
      }
      post {
        always {
          junit allowEmptyResults: true, testResults: "${REPORT_DIR}/*.xml"
        }
      }
    }

    stage('Build package (optional)') {
      steps {
        script {
          if (isUnix()) {
            sh '''
              set -e
              if [ -f pyproject.toml ] || [ -f setup.py ]; then
                ${VENV}/bin/python -m pip install -U build || true
                rm -rf ${DIST_DIR} || true
                ${VENV}/bin/python -m build --outdir ${DIST_DIR} || true
              else
                echo "No pyproject.toml or setup.py found; skipping build"
              fi
            '''
            archiveArtifacts artifacts: "${DIST_DIR}/**", allowEmptyArchive: true
          } else {
            bat '''
            @echo off
            set BUILD_OK=0
            if exist pyproject.toml set BUILD_OK=1
            if exist setup.py set BUILD_OK=1
            if %BUILD_OK%==1 (
              "%VENV%\\Scripts\\python.exe" -m pip install -U build || exit /b 0
              if exist %DIST_DIR% rmdir /s /q %DIST_DIR%
              "%VENV%\\Scripts\\python.exe" -m build --outdir %DIST_DIR% || exit /b 0
            ) else (
              echo No pyproject.toml or setup.py found; skipping build
            )
            '''
            archiveArtifacts artifacts: "${DIST_DIR}\\\\**", allowEmptyArchive: true
          }
        }
      }
    }

    stage('Run script (example)') {
      steps {
        script {
          if (isUnix()) {
            sh '''
              if [ -f main.py ]; then
                ${VENV}/bin/python main.py
              else
                echo "main.py not found; skipping run"
              fi
            '''
          } else {
            bat '''
            @echo off
            if exist main.py (
              "%VENV%\\Scripts\\python.exe" main.py
            ) else (
              echo main.py not found; skipping run
            )
            '''
          }
        }
      }
    }
  } // stages

  post {
    success { echo "Pipeline succeeded" }
    unstable { echo "Pipeline finished with unstable results" }
    failure { echo "Pipeline failed" }
    always { cleanWs() }
  }
}
