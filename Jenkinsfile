pipeline {
  agent any

  environment {
    // Change to a UNC share like "\\\\MY-PC\\JenkinsShare" if you want to copy to your PC across the network
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

REM safe echo without ampersand
echo Done prepare and build
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

    stage('Copy all project files to BUILD_OUTPUT') {
      steps {
        script {
          echo "Resolved BUILD_OUTPUT (Groovy): ${env.BUILD_OUTPUT}"
          bat """
@echo off
set SRC=%WORKSPACE%
set DEST="C:\\Users\\swethasuresh\\testing"

echo ============================================
echo Copying all files from:
echo   %SRC%
echo to:
echo   "C:\\Users\\swethasuresh\\testing"
echo ============================================

REM Ensure destination exists
if not exist "%DEST%" (
  echo Creating destination folder...
  mkdir "%DEST%"
)

REM Copy everything except .git, venv, and the artifact folder
robocopy "%SRC%" "%DEST%" /E /XO /R:2 /W:2 /XD "%SRC%\\.git" "%SRC%\\venv" "%SRC%\\build_artifacts" /NFL /NDL /NP /V
set RC=%ERRORLEVEL%

echo Robocopy exit code: %RC%
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
  } // end stages

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
} // end pipeline
