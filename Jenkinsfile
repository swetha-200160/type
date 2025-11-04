pipeline {
  agent any

  environment {
    // use forward slashes in Groovy strings but Windows commands will use backslashes
    VENV = "${WORKSPACE}/venv"
    BUILD_DIR = "${WORKSPACE}/build"
    PERSISTENT_DIR = "D:/testproject/Html/jenkins-artifacts"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Debug before build') {
      steps {
        bat '''
        @echo off
        echo ==== DEBUG BEFORE BUILD ====
        echo Running on: %COMPUTERNAME%
        echo WORKSPACE=%WORKSPACE%
        dir "%WORKSPACE%" /A
        '''
      }
    }

    stage('Create venv & install deps') {
      steps {
        bat '''
        @echo off
        REM create venv if not exists (try py then python)
        if not exist "%VENV%" (
          py -3 -m venv "%VENV%" >NUL 2>&1 || python -m venv "%VENV%" >NUL 2>&1
        )

        REM ensure pip and tools are up to date
        "%VENV%\\Scripts\\python.exe" -m pip install --upgrade pip setuptools wheel

        REM install requirements if file exists
        if exist requirements.txt (
          "%VENV%\\Scripts\\pip.exe" install -r requirements.txt
        ) else (
          echo "No requirements.txt found; skipping pip install"
        )
        '''
      }
    }

    stage('Train & Build') {
      steps {
        bat '''
        @echo off
        echo ==== TRAIN & BUILD ====
        REM ensure build dir exists
        powershell -NoProfile -Command "New-Item -ItemType Directory -Force -Path '%BUILD_DIR%' | Out-Null"

        REM run training if script exists
        if exist src\\model\\train.py (
          "%VENV%\\Scripts\\python.exe" src\\model\\train.py
        ) else (
          echo "Warning: src\\model\\train.py not found; skipping training"
        )

        REM create artifact zip using PowerShell (single -Command invocation; no caret line-continuations)
        powershell -NoProfile -Command "if (Test-Path 'src' -or Test-Path 'README.md') { $paths = @(); if (Test-Path 'src') { $paths += 'src' }; if (Test-Path 'README.md') { $paths += 'README.md' }; Compress-Archive -Path $paths -DestinationPath (Join-Path -Path '%BUILD_DIR%' -ChildPath 'project.zip') -Force; Write-Host 'Created %BUILD_DIR%\\project.zip' } else { Write-Error 'Nothing to archive (no src or README.md)'; exit 1 }"

        echo "Build directory listing:"
        dir "%BUILD_DIR%" /A
        '''
      }
    }

    stage('Archive') {
      steps {
        // archive build artifacts for Jenkins UI; allowEmptyArchive true prevents job failure if build dir absent
        archiveArtifacts artifacts: 'build/**', allowEmptyArchive: true
      }
    }

    stage('Persist locally (robocopy)') {
      steps {
        bat '''
        @echo off
        echo ==== COPY TO PERSISTENT DIR (robocopy) ====
        echo PERSISTENT_DIR=%PERSISTENT_DIR%

        REM ensure persistent root exists
        powershell -NoProfile -Command "New-Item -ItemType Directory -Force -Path '%PERSISTENT_DIR%' | Out-Null"

        REM prepare destination for this job/build
        set DEST=%PERSISTENT_DIR%\\%JOB_NAME%\\%BUILD_NUMBER%_build\\build
        powershell -NoProfile -Command "New-Item -ItemType Directory -Force -Path '%DEST%' | Out-Null"

        REM check build dir exists and not empty
        if not exist "%BUILD_DIR%" (
          echo ERROR: Build directory not found: %BUILD_DIR%
          exit /b 2
        )

        REM run robocopy (mirror, copy data/attrs/timestamps, retry 3 times, wait 5s)
        robocopy "%BUILD_DIR%" "%DEST%" /MIR /COPY:DAT /R:3 /W:5 /NP /NFL /NDL
        set RC=%ERRORLEVEL%
        echo robocopy exit code: %RC%

        REM robocopy exit codes: 0-7 are success/warn, >=8 is failure
        if %RC% GEQ 8 (
          echo ERROR: robocopy failed with exit code %RC%
          exit /b %RC%
        ) else (
          echo "robocopy completed with exit code %RC% (treated as success)"
        )

        echo "Destination listing:"
        dir "%DEST%" /A
        '''
      }
    }

    stage('Debug after copy') {
      steps {
        bat '''
        @echo off
        echo ==== FINAL WORKSPACE LISTING TOP ====
        dir "%WORKSPACE%" /A
        '''
      }
    }
  }

  post {
    success { echo "Pipeline succeeded" }
    failure { echo "Pipeline failed — check console output" }
    always { echo "Finished" }
  }
}
