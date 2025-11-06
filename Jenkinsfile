pipeline {
  agent any

  environment {
    BUILD_OUTPUT = "C:\\Users\\swethasuresh\\testing"
    // change SOURCE_SUBFOLDER if you want a different folder copied (relative to workspace)
    SOURCE_SUBFOLDER = "C:\\Users\\swethasuresh\\Desktop\\text.code"
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

REM create venv if needed
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

REM Run train.py if present
if exist "%WORKSPACE%\\train.py" (
  echo Running "%WORKSPACE%\\train.py"
  python "%WORKSPACE%\\train.py"
) else if exist "%WORKSPACE%\\src\\model\\train.py" (
  echo Running "%WORKSPACE%\\src\\model\\train.py"
  python "%WORKSPACE%\\src\\model\\train.py"
) else (
  echo No train.py found - skipping training
)

echo Done prepare and build
'''
      }
    }

    stage('Copy selected folder to BUILD_OUTPUT') {
      steps {
        script {
          // Expand Groovy env vars into the batch script
          def dest = env.BUILD_OUTPUT.replaceAll('\\\\','\\\\\\\\') // keep readable if needed
          def sub = env.SOURCE_SUBFOLDER
          echo "Will try to copy workspace subfolder: ${sub} to ${env.BUILD_OUTPUT}"
          bat """
@echo off
setlocal
set SRC=%WORKSPACE%\\${sub}
set DEST="${env.BUILD_OUTPUT}"

echo =====================================================
echo Trying to copy folder: %SRC%
echo Destination root: %DEST%
echo =====================================================

REM If the specified subfolder exists, copy that folder only
if exist "%SRC%" (
  echo Source subfolder found. Copying "%SRC%" -> "%DEST%\\${sub.replaceAll('\\\\','\\\\\\')%2F}"
  REM Ensure destination exists
  if not exist %DEST% mkdir %DEST%
  REM Create parent path for subfolder inside destination
  REM Copy the contents of the subfolder into DEST\\<subfolder-name>
  robocopy "%SRC%" "%DEST%\\${sub.replaceAll('\\\\','\\\\')}" /E /COPY:DAT /DCOPY:T /R:2 /W:2 /NFL /NDL /NP /V
  set RC=%ERRORLEVEL%
  echo robocopy (subfolder -> dest) exit code: %RC%
  if %RC% LEQ 7 (
    echo Subfolder copy succeeded.
    endlocal
    exit /b 0
  ) else (
    echo Subfolder copy failed with code %RC%.
    endlocal
    exit /b %RC%
  )
) else (
  echo Subfolder not found: "%SRC%". Falling back to copying whole workspace.
  REM Copy entire workspace (exclude .git, venv, build_artifacts)
  set SRCROOT=%WORKSPACE%
  if not exist %DEST% mkdir %DEST%
  robocopy "%SRCROOT%" "%DEST%" /E /COPY:DAT /DCOPY:T /R:2 /W:2 /XD "%SRCROOT%\\.git" "%SRCROOT%\\venv" "%SRCROOT%\\build_artifacts" /NFL /NDL /NP /V
  set RC=%ERRORLEVEL%
  echo robocopy (workspace -> dest) exit code: %RC%
  if %RC% LEQ 7 (
    echo Workspace copy succeeded.
    endlocal
    exit /b 0
  ) else (
    echo Workspace copy failed with code %RC%.
    endlocal
    exit /b %RC%
  )
)
"""
        }
      }
    }
  } // end stages

  post {
    success {
      echo "Files copied to BUILD_OUTPUT (if this agent can write to that path)."
      echo "Note: BUILD_OUTPUT is on the agent that ran the job (check 'Running on' at top of Console Output)."
    }
    failure {
      echo "Pipeline failed — check Console Output for robocopy exit codes and errors."
    }
  }
}
