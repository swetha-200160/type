ipeline {
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
                script {
                    bat """
@echo off
set ARTIFACT_DIR=%WORKSPACE%\\build_artifacts
 
if exist "%ARTIFACT_DIR%" rmdir /S /Q "%ARTIFACT_DIR%"
mkdir "%ARTIFACT_DIR%"
 
REM copy model file if present
if exist "%WORKSPACE%\\src\\model\\model.pkl" (
  copy "%WORKSPACE%\\src\\model\\model.pkl" "%ARTIFACT_DIR%\\"
)
 
REM copy entire model folder if you want
if exist "%WORKSPACE%\\src\\model" (
  xcopy "%WORKSPACE%\\src\\model\\" "%ARTIFACT_DIR%\\model\\" /E /I /Y
)
 
REM copy dist folder
if exist "%WORKSPACE%\\dist" (
  xcopy "%WORKSPACE%\\dist\\" "%ARTIFACT_DIR%\\dist\\" /E /I /Y
)
 
REM copy other useful files
if exist "%WORKSPACE%\\requirements.txt" copy "%WORKSPACE%\\requirements.txt" "%ARTIFACT_DIR%\\"
if exist "%WORKSPACE%\\train.log" copy "%WORKSPACE%\\train.log" "%ARTIFACT_DIR%\\"
 
echo Artifacts prepared under %ARTIFACT_DIR%
dir "%ARTIFACT_DIR%"
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
 