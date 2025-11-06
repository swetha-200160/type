pipeline {
  agent any

  environment {
    // If you want to copy directly to your PC across the network, replace with UNC like "\\\\MY-PC\\JenkinsShare"
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
        echo 'Prepare environment and run train/build if present'
        bat '''
@echo off
cd /D "%WORKSPACE%"

REM create venv if needed
if not exist "venv\\Scripts\\python.exe" (
  echo Creating venv...
  py -3 -m venv venv
)
call "venv\\Scripts\\activate"

echo Upgrading pip...
python -m pip install --upgrade pip

if exist "requirements.txt" (
  echo Installing requirements...
  pip install -r "requirements.txt"
) else (
  echo No requirements.txt; installing minimal deps...
  pip install scikit-learn joblib
)

REM Run train.py if it exists (prefer workspace root)
if exist "%WORKSPACE%\\train.py" (
  echo Running "%WORKSPACE%\\train.py"
  python "%WORKSPACE%\\train.py"
) else if exist "%WORKSPACE%\\src\\model\\train.py" (
  echo Running "%WORKSPACE%\\src\\model\\train.py"
  python "%WORKSPACE%\\src\\model\\train.py"
) else (
  echo No train.py found - skipping training run
)

echo Done prepare & build
'''
      }
    }

    stage('Collect all workspace files into build_artifacts') {
      steps {
        echo 'Copying whole workspace (excluding .git) into build_artifacts...'
        bat """
@echo off
set SRC=%WORKSPACE%
set ART_DIR=%WORKSPACE%\\build_artifacts

REM remove old artifacts and recreate
if exist "%ART_DIR%" rmdir /S /Q "%ART_DIR%"
mkdir "%ART_DIR%"

REM Mirror workspace -> build_artifacts excluding .git and excluding the artifact folder itself
robocopy "%SRC%" "%ART_DIR%" /MIR /XD "%SRC%\\.git" "%ART_DIR%" /R:2 /W:2 /NFL /NDL

set RC=%ERRORLEVEL%
echo Robocopy (workspace -> build_artifacts) exit code: %RC%

echo ==== build_artifacts CONTENTS ====
dir /S "%ART_DIR%"
"""
      }
    }

    stage('Copy build_artifacts to BUILD_OUTPUT') {
      steps {
        script {
          echo "Resolved BUILD_OUTPUT (Groovy): ${env.BUILD_OUTPUT}"
          bat """
@echo off
set ART_DIR=%WORKSPACE%\\build_artifacts
set DEST=${env.BUILD_OUTPUT}

if not exist "%ART_DIR%" (
  echo ERROR: %ART_DIR% does not exist - nothing to copy
  exit /b 5
)

REM Ensure destination exists on the agent
if not exist "%DEST%" (
  echo Creating destination: %DEST%
  mkdir "%DEST%"
) else (
  echo Destination exists: %DEST%
)

REM Copy artifacts to destination (preserve timestamps)
robocopy "%ART_DIR%" "%DEST%" /E /COPY:DAT /DCOPY:T /R:2 /W:2 /NFL /NDL /NP /V
set RC=%ERRORLEVEL%
echo Robocopy (build_artifacts -> DEST) exit code: %RC%

REM robocopy codes 0-7 are OK
if %RC% LEQ 7 (
  echo Copy succeeded with code %RC%
  exit /b 0
)

echo Copy failed with code %RC%
exit /b %RC%
"""
        }
      }
    }
  }

  post {
    always {
      // archive artifacts so you can download them from Jenkins UI
      archiveArtifacts artifacts: 'build_artifacts/**', allowEmptyArchive: false
    }
    success {
      echo 'Pipeline completed: artifacts copied and archived (if present).'
    }
    failure {
      echo 'Pipeline failed — check Console Output for details.'
    }
  }
}
