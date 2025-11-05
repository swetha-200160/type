pipeline {
  agent any

  environment {
    // Groovy-friendly forward slashes; Windows commands in bat use backslashes
    VENV = "${WORKSPACE}/venv"
    BUILD_DIR = "${WORKSPACE}/build"
    PERSISTENT_DIR = "D:/testproject/Html/jenkins-artifact" // <<< your exact destination
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Debug before build') {
      steps {
        bat '''
        @echo off
        echo ==== DEBUG BEFORE BUILD ====
        echo Running on: %COMPUTERNAME%
        echo WORKSPACE=%WORKSPACE%
        dir "%WORKSPACE%" /A /S > "%WORKSPACE%\\workspace_before_list.txt"
        type "%WORKSPACE%\\workspace_before_list.txt"
        '''
      }
    }

    stage('Create venv & install deps') {
      steps {
        bat '''
        @echo off
        REM create venv if not exists (try py then python)
        if not exist "%VENV%\\Scripts\\python.exe" (
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

        REM Attempt to run train.py from workspace root OR src\model\train.py
        if exist "%WORKSPACE%\\train.py" (
          echo "Running workspace root train.py"
          "%VENV%\\Scripts\\python.exe" "%WORKSPACE%\\train.py"
        ) else if exist "%WORKSPACE%\\src\model\train.py" (
          echo "Running src\\model\\train.py"
          "%VENV%\\Scripts\\python.exe" "%WORKSPACE%\\src\\model\\train.py"
        ) else (
          echo "Warning: no train.py found at workspace root or src\\model\\train.py; skipping training"
        )

        REM create artifact zip using PowerShell if there's something to archive
        powershell -NoProfile -Command ^
          "if (Test-Path 'src' -or Test-Path 'README.md') { $paths=@(); if (Test-Path 'src') {$paths += 'src'}; if (Test-Path 'README.md') {$paths += 'README.md'}; Compress-Archive -Path $paths -DestinationPath (Join-Path -Path '%BUILD_DIR%' -ChildPath 'project.zip') -Force; Write-Host 'Created %BUILD_DIR%\\project.zip' } else { Write-Host 'Nothing to archive (no src or README.md)'; }"

        echo "Build directory listing (after build):"
        dir "%BUILD_DIR%" /A /S > "%WORKSPACE%\\build_before_copy_list.txt"
        type "%WORKSPACE%\\build_before_copy_list.txt"
        '''
      }
    }

    stage('Archive') {
      steps {
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

        REM prepare destination for this job/build (per-build folder)
        set DEST=%PERSISTENT_DIR%\\%JOB_NAME%\\%BUILD_NUMBER%_build
        echo Creating dest: %DEST%
        powershell -NoProfile -Command "New-Item -ItemType Directory -Force -Path '%DEST%' | Out-Null"

        REM check build dir exists and not empty
        if not exist "%BUILD_DIR%" (
          echo ERROR: Build directory not found: %BUILD_DIR%
          exit /b 2
        )

        REM short wait to ensure files are flushed to disk
        timeout /T 2 /NOBREAK >NUL

        REM show what we will copy
        dir "%BUILD_DIR%" /A /S > "%WORKSPACE%\\workspace_build_list_for_copy.txt"
        type "%WORKSPACE%\\workspace_build_list_for_copy.txt"

        REM run robocopy: copy everything under build into DEST. /E includes subfolders and empty dirs.
        REM /COPY:DAT copies data, attributes, timestamps. /R:3 /W:5 retry settings. /V verbose. /LOG writes details.
        robocopy "%BUILD_DIR%" "%DEST%" /E /COPY:DAT /R:3 /W:5 /V /ETA /LOG:"%WORKSPACE%\\robocopy_log.txt"

        set RC=%ERRORLEVEL%
        echo robocopy exit code: %RC%
        type "%WORKSPACE%\\robocopy_log.txt"

        REM Treat 0..7 as success-ish; fail for >=8
        if %RC% GEQ 8 (
          echo ERROR: robocopy failed with exit code %RC%
          exit /b %RC%
        ) else (
          echo "robocopy completed with exit code %RC% (treated as success)"
        )

        echo "Destination listing (after copy):"
        dir "%DEST%" /A /S > "%WORKSPACE%\\dest_after_copy_list.txt"
        type "%WORKSPACE%\\dest_after_copy_list.txt"
        '''
      }
    }

    stage('Debug after copy') {
      steps {
        bat '''
        @echo off
        echo ==== FINAL WORKSPACE LISTING TOP ====
        dir "%WORKSPACE%" /A /S > "%WORKSPACE%\\workspace_final_list.txt"
        type "%WORKSPACE%\\workspace_final_list.txt"
        '''
      }
    }
  }

  post {
    success { echo "Pipeline succeeded" }
    failure { echo "Pipeline failed — check console output" }
    always {
      // archive debug logs so you can inspect them from the Jenkins UI
      archiveArtifacts artifacts: 'workspace_before_list.txt, build_before_copy_list.txt, workspace_build_list_for_copy.txt, robocopy_log.txt, dest_after_copy_list.txt, workspace_final_list.txt', allowEmptyArchive: true
      echo "Finished"
    }
  }
}
