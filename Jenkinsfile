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
    echo ==== COPY TO LOCAL (robocopy) ====
    echo Copying from %BUILD_DIR% to %PERSISTENT_DIR%

    REM === Create the destination folder if it doesn't exist ===
    powershell -NoProfile -Command "New-Item -ItemType Directory -Force -Path '%PERSISTENT_DIR%' | Out-Null"

    REM === Copy everything (files + folders) from Jenkins build directory ===
    REM /E copies all subdirectories (even empty)
    REM /COPYALL copies all attributes (data, timestamps, permissions, etc.)
    REM /R:1 /W:1 retries once, waits 1 sec
    REM /V shows verbose details
    robocopy "%WORKSPACE%" "%PERSISTENT_DIR%" *.* /E /COPYALL /R:1 /W:1 /V

    echo ==== AFTER COPY ====
    dir "%PERSISTENT_DIR%" /S /A
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
 
 