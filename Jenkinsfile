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
 
        stage('Build') {
            steps {
                echo 'Building Python project...'
                bat '''
@echo off
echo ==== PYTHON BUILD START ====
 
REM Use workspace variable - safer than hard-coded paths
setlocal
 
REM create venv if needed
if not exist "venv\\Scripts\\python.exe" (
    py -3 -m venv venv
)
call "venv\\Scripts\\activate"
 
python -m pip install --upgrade pip
 
if exist "requirements.txt" (
    pip install -r "requirements.txt"
) else (
    pip install scikit-learn joblib
)
 
REM Prefer workspace train.py
if exist "%WORKSPACE%\\train.py" (
    echo Running "%WORKSPACE%\\train.py"
    python "%WORKSPACE%\\train.py"
) else (
    REM Try alternative path - NOTE: must point to a .py script
    if exist "C:\\ProgramData\\python pjt\\src\\model\\train.py" (
        echo Running "C:\\ProgramData\\python pjt\\src\\model\\train.py"
        python "C:\\ProgramData\\python pjt\\src\\model\\train.py"
    ) else (
        echo No train.py found in workspace or alternate path
        exit /b 0
    )
)
 
endlocal
echo ==== PYTHON BUILD END ====
'''
            }
        }
 
        stage('Debug - list outputs') {
            steps {
                bat '''
@echo off
echo ====== WORKSPACE ROOT ======
dir /B "%WORKSPACE%"
 
echo ====== src\\model ======
if exist "%WORKSPACE%\\src\\model" (
  dir /S "%WORKSPACE%\\src\\model"
) else (
  echo src\\model not present
)
 
echo ====== build_artifacts preview (if exists) ======
if exist "%WORKSPACE%\\build_artifacts" (
  dir /S "%WORKSPACE%\\build_artifacts"
) else (
  echo build_artifacts not present yet
)
'''
            }
        }
 
        stage('Gather Artifacts') {
  steps {
    bat """
@echo off
echo ==== GATHER ARTIFACTS ====
echo WORKSPACE=%WORKSPACE%
set ARTIFACT_DIR=%WORKSPACE%\\build_artifacts

REM remove old and create new
if exist "%ARTIFACT_DIR%" (
  echo Removing existing %ARTIFACT_DIR%
  rmdir /S /Q "%ARTIFACT_DIR%"
)
mkdir "%ARTIFACT_DIR%"

REM copy model and folders (only if exist)
if exist "%WORKSPACE%\\src\\model\\model.pkl" (
  echo Copying model.pkl
  copy "%WORKSPACE%\\src\\model\\model.pkl" "%ARTIFACT_DIR%\\"
)

if exist "%WORKSPACE%\\src\\model" (
  echo Copying full src\\model folder
  xcopy "%WORKSPACE%\\src\\model\\" "%ARTIFACT_DIR%\\model\\" /E /I /Y
)

if exist "%WORKSPACE%\\dist" (
  echo Copying dist folder
  xcopy "%WORKSPACE%\\dist\\" "%ARTIFACT_DIR%\\dist\\" /E /I /Y
)

if exist "%WORKSPACE%\\requirements.txt" copy "%WORKSPACE%\\requirements.txt" "%ARTIFACT_DIR%\\"
if exist "%WORKSPACE%\\train.log" copy "%WORKSPACE%\\train.log" "%ARTIFACT_DIR%\\"

echo ==== ARTIFACT_DIR CONTENTS ====
dir "%ARTIFACT_DIR%"
"""
  }
}

stage('Copy Artifacts to Target') {
  steps {
    script {
      // show exact groovy-expanded path in pipeline log
      echo "Resolved BUILD_OUTPUT (Groovy): ${env.BUILD_OUTPUT}"

      bat """
@echo off
echo ==== COPY TO TARGET ====
set ARTIFACT_DIR=%WORKSPACE%\\build_artifacts
echo ARTIFACT_DIR=%ARTIFACT_DIR%
echo BUILD_OUTPUT=${env.BUILD_OUTPUT}

REM Make sure artifact dir exists and is not empty
if not exist "%ARTIFACT_DIR%" (
  echo ERROR: Artifact dir does not exist: %ARTIFACT_DIR%
  exit /b 1
)

REM list files to copy
dir /S "%ARTIFACT_DIR%"

REM Ensure destination exists (create)
if not exist "${env.BUILD_OUTPUT}" (
  echo Creating destination ${env.BUILD_OUTPUT}
  mkdir "${env.BUILD_OUTPUT}"
) else (
  echo Destination already exists
)

REM Robocopy - copy files and subfolders, preserve timestamps, retry minimal
robocopy "%ARTIFACT_DIR%" "${env.BUILD_OUTPUT}" /E /COPY:DAT /DCOPY:T /R:2 /W:2 /NFL /NDL /NP /V

set RC=%ERRORLEVEL%
echo Robocopy exit code: %RC%

REM treat 0-7 as success per robocopy docs
if %RC% LEQ 7 (
  echo Robocopy succeeded with code %RC%
  exit /b 0
)

echo Robocopy failed with code %RC%
exit /b %RC%
"""
    }
  }
}

 
        stage('Copy Artifacts to Target') {
            steps {
                script {
                    bat """
@echo off
set ARTIFACT_DIR=%WORKSPACE%\\build_artifacts
 
if not exist "${env.BUILD_OUTPUT}" mkdir "${env.BUILD_OUTPUT}"
 
robocopy "%ARTIFACT_DIR%" "${env.BUILD_OUTPUT}" /E /XO /R:2 /W:2 /NFL /NDL
 
set RC=%ERRORLEVEL%
echo Robocopy exit code: %RC%
if %RC% LEQ 7 (
  echo Robocopy finished with acceptable code %RC%. Exiting success.
  exit /b 0
)
echo Robocopy FAILED with code %RC%. Exiting with failure.
exit /b %RC%
"""
                }
            }
        }
    }
 
    post {
        success {
            echo 'Build completed successfully and artifacts copied to target folder'
        }
        failure {
            echo 'Build or copy failed!'
        }
    }
}
 
 