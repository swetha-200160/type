pipeline {
  agent any

  environment {
    VENV = "%WORKSPACE%C:\ProgramData\Jenkins\.jenkins\workspace\jenkins pipeline\ven"
    BUILD_DIR = "%WORKSPACE%C:\ProgramData\Jenkins\.jenkins\workspace\jenkins pipeline\build"
    PERSISTENT_DIR = "C:\\jenkins-artifacts"   // <-- change to an accessible path on the Windows agent
  }

  options {
    timestamps()
    disableConcurrentBuilds()
    buildDiscarder(logRotator(daysToKeepStr: '14'))
  }

  stages {
    stage('Checkout') { steps { checkout scm } }

    stage('Agent diagnostics') {
      steps {
        bat '''
          @echo off
          echo Running on: %COMPUTERNAME%
          echo Workspace: %WORKSPACE%
          echo User: %USERNAME%
          where python >nul 2>&1 && where py >nul 2>&1
          py -3 --version 2>nul || python --version 2>nul || echo no python found
        '''
      }
    }

    stage('Create venv & install') {
      steps {
        bat '''
          @echo off
          setlocal
          set PY_CMD=
          where py >nul 2>&1
          if %ERRORLEVEL%==0 ( set PY_CMD=py -3 ) else (
            where python >nul 2>&1
            if %ERRORLEVEL%==0 ( set PY_CMD=python ) else (
              echo ERROR: No python found on PATH
              exit /b 1
            )
          )
          echo Using %PY_CMD%
          %PY_CMD% -m venv "%WORKSPACE%\\venv"
          "%WORKSPACE%\\venv\\Scripts\\python.exe" -m pip install --upgrade pip setuptools wheel
          if exist requirements.txt (
            "%WORKSPACE%\\venv\\Scripts\\pip.exe" install -r requirements.txt
          )
          endlocal
        '''
      }
    }

    stage('Train & Build') {
      steps {
        bat '''
          @echo off
          if exist "%WORKSPACE%\\build" rmdir /s /q "%WORKSPACE%\\build"
          mkdir "%WORKSPACE%\\build"
          "%WORKSPACE%\\venv\\Scripts\\python.exe" src\\model\\train.py || echo training script returned non-zero
          REM If you have a build.bat, call it. If only build.sh exists, use PowerShell to zip.
          if exist build.bat (
            call build.bat
          ) else (
            powershell -Command "Compress-Archive -Path src,README.md,requirements.txt,Jenkinsfile -DestinationPath '%WORKSPACE%\\build\\ai-python-project-%DATE:~-4,4%%DATE:~4,2%%DATE:~7,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%.zip' -Force"
          )
          dir "%WORKSPACE%\\build"
        '''
      }
    }

    stage('Archive artifacts') {
      steps {
        archiveArtifacts artifacts: 'build\\\\**', allowEmptyArchive: true, fingerprint: true
      }
    }

    stage('Copy to persistent local path') {
      steps {
        bat '''
          @echo off
          set DEST=%PERSISTENT_DIR%\\%JOB_NAME%\\%BUILD_NUMBER%_build
          if not exist "%PERSISTENT_DIR%\\%JOB_NAME%" mkdir "%PERSISTENT_DIR%\\%JOB_NAME%"
          if exist "%DEST%" rmdir /s /q "%DEST%"
          xcopy "%WORKSPACE%\\build" "%DEST%\\build" /E /I /Y
          echo Copied build to %DEST%
          dir "%DEST%"
        '''
      }
    }

    stage('Debug final workspace') {
      steps {
        bat 'dir %WORKSPACE% /S | more'
      }
    }
  }

  post {
    success { echo "Pipeline succeeded" }
    unstable { echo "Pipeline unstable" }
    failure { echo "Pipeline failed" }
    always {
      echo "Workspace left intact for debugging. Remove this and enable cleanWs() later to clean."
      // cleanWs()
    }
  }
}
