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

    stage('Prepare & Build') {
      steps {
        echo 'Prepare environment and run train.py (if present)'
        bat '''
@echo off
cd /D "%WORKSPACE%"

REM create venv if missing
if not exist "venv\\Scripts\\python.exe" (
  echo Creating venv...
  py -3 -m venv venv
)
call "venv\\Scripts\\activate"

echo Upgrading pip...
python -m pip install --upgrade pip

if exist "%WORKSPACE%\\requirements.txt" (
  echo Installing requirements...
  pip install -r "%WORKSPACE%\\requirements.txt"
) else (
  echo No requirements.txt; installing minimal deps...
  pip install scikit-learn joblib
)

REM Run train.py if present (optional)
if exist "%WORKSPACE%\\train.py" (
  echo Running train.py...
  python "%WORKSPACE%\\train.py"
) else (
  echo No train.py found - skipping training step
)

echo Done prepare and build
'''
      }
    }

    stage('Collect: mirror workspace to build_artifacts') {
      steps {
        echo 'Mirroring whole workspace to build_artifacts (excluding .git & venv)...'
        bat """
@echo off
set SRC=%WORKSPACE%
set ART=%WORKSPACE%\\build_artifacts

if exist "%ART%" rmdir /S /Q "%ART%"
mkdir "%ART%"

robocopy "%SRC%" "%ART%" /MIR /XD "%SRC%\\.git" "%SRC%\\venv" "%ART%" /R:2 /W:2 /NFL /NDL
set RC=%ERRORLEVEL%
echo Robocopy (workspace -> build_artifacts) exit code: %RC%

echo ==== build_artifacts listing ====
dir /S "%ART%"

exit /b %RC%
"""
      }
    }

    stage('Copy everything to BUILD_OUTPUT') {
      steps {
        script {
          echo "Resolved BUILD_OUTPUT: ${env.BUILD_OUTPUT}"
          bat """
@echo off
set SRC=%WORKSPACE%\\build_artifacts
set DEST=${env.BUILD_OUTPUT}

if not exist "%SRC%" (
  echo ERROR: %SRC% does not exist
  exit /b 4
)

if not exist "%DEST%" (
  echo Creating destination %DEST%
  mkdir "%DEST%"
) else (
  echo Destination already exists: %DEST%
)

robocopy "%SRC%" "%DEST%" /E /COPY:DAT /DCOPY:T /R:2 /W:2 /XO /NFL /NDL /NP /V
set RC=%ERRORLEVEL%
echo Robocopy (build_artifacts -> DEST) exit code: %RC%

if %RC% LEQ 7 (
  echo Copy succeeded with code %RC%
  exit /b 0
) else (
  echo Copy failed with code %RC%
  exit /b %RC%
)
"""
        }
      }
    }
  }

  post {
    success {
      echo "Build finished. Files mirrored to ${env.BUILD_OUTPUT} on the agent."
    }
    failure {
      echo "Pipeline failed — inspect Console Output for errors."
    }
  }
}
