pipeline {
    agent any

    environment {
        BUILD_OUTPUT = "C:\\Users\\swethasuresh\\testing"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'master',
                    credentialsId: 'gitrepo',
                    url: 'https://github.com/swetha-200160/type.git'
            }
        }

        stage('Build (venv + run Project.py)') {
            steps {
                echo 'Creating venv, installing requirements, and running Project.py (if present)...'
                bat '''
@echo off
echo ==== BUILD START ====
setlocal

REM create venv if needed
if not exist "venv\\Scripts\\python.exe" (
    py -3 -m venv venv
)

call "venv\\Scripts\\activate"

python -m pip install --upgrade pip

if exist "requirements.txt" (
    echo Installing from requirements.txt
    pip install -r "requirements.txt"
) else (
    echo requirements.txt not found — skipping pip install
)

REM Run Project.py if it exists in workspace root
if exist "%WORKSPACE%\\Project.py" (
    echo Running Project.py
    python "%WORKSPACE%\\Project.py"
) else (
    echo Project.py not found in workspace root — skipping run
)

endlocal
echo ==== BUILD END ====
'''
            }
        }

        stage('Debug - list workspace') {
            steps {
                bat '''
@echo off
echo ====== WORKSPACE LISTING ======
dir "%WORKSPACE%" /B
echo ====== DETAILED ======
dir "%WORKSPACE%"
'''
            }
        }

        stage('Gather Build Files (zip)') {
            steps {
                bat """
@echo off
echo ==== GATHER BUILD FILES INTO ZIP ====
set ARTIFACT_DIR=%WORKSPACE%\\build_artifacts

REM Remove old artifact folder and recreate
if exist "%ARTIFACT_DIR%" (
  echo Removing existing %ARTIFACT_DIR%
  rmdir /S /Q "%ARTIFACT_DIR%"
)
mkdir "%ARTIFACT_DIR%"

REM Prepare list of files to include
set INCLUDE_LIST=
if exist "%WORKSPACE%\\AI-Data.csv" set INCLUDE_LIST=%INCLUDE_LIST% "%WORKSPACE%\\AI-Data.csv"
if exist "%WORKSPACE%\\Project.py" set INCLUDE_LIST=%INCLUDE_LIST% "%WORKSPACE%\\Project.py"
if exist "%WORKSPACE%\\requirements.txt" set INCLUDE_LIST=%INCLUDE_LIST% "%WORKSPACE%\\requirements.txt"
if exist "%WORKSPACE%\\README.md" set INCLUDE_LIST=%INCLUDE_LIST% "%WORKSPACE%\\README.md"

if "%INCLUDE_LIST%"=="" (
  echo No build files found to package.
) else (
  REM Use PowerShell Compress-Archive to create a single zip with only the selected files
  powershell -NoProfile -Command "Remove-Item -Force -ErrorAction SilentlyContinue '%ARTIFACT_DIR%\\build_files.zip'; Compress-Archive -Path %INCLUDE_LIST% -DestinationPath '%ARTIFACT_DIR%\\build_files.zip' -Force"
  if exist "%ARTIFACT_DIR%\\build_files.zip" (
    echo Created %ARTIFACT_DIR%\\build_files.zip
  ) else (
    echo Failed to create build_files.zip
    exit /b 1
  )
)

echo ==== ARTIFACT_DIR CONTENTS ====
dir "%ARTIFACT_DIR%"
"""
            }
        }

        stage('Copy build zip to target') {
            steps {
                script {
                    bat """
@echo off
echo ==== COPY BUILD ZIP TO TARGET ====
set ARTIFACT_DIR=%WORKSPACE%\\build_artifacts
set TARGET_DIR=${env.BUILD_OUTPUT}

if not exist "%ARTIFACT_DIR%" (
  echo Artifact dir missing: %ARTIFACT_DIR%
  exit /b 1
)

if not exist "%TARGET_DIR%" (
  echo Creating target dir: %TARGET_DIR%
  mkdir "%TARGET_DIR%"
)

REM Copy only the build zip
robocopy "%ARTIFACT_DIR%" "%TARGET_DIR%" build_files.zip /S /XO /R:2 /W:2 /NFL /NDL

set RC=%ERRORLEVEL%
echo Robocopy exit code: %RC%
if %RC% LEQ 7 (
  echo build_files.zip copied successfully to %TARGET_DIR%.
  exit /b 0
)
echo Copy failed with code %RC%.
exit /b %RC%
"""
                }
            }
        }
    }

    post {
        success {
            echo 'Build completed and build_files.zip copied to target folder.'
        }
        failure {
            echo 'Build or copy failed!'
        }
    }
}
