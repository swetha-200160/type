pipeline {
  agent any

  environment {
    VENV = "${WORKSPACE}/venv"
    BUILD_DIR = "${WORKSPACE}/build"
    PERSISTENT_DIR = "D:/testproject/Html/jenkins-artifacts"
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
        "%VENV%\\Scripts\\python.exe" -m pip install --upgrade pip setuptools wheel
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
        powershell -NoProfile -Command "New-Item -ItemType Directory -Force -Path '%BUILD_DIR%' | Out-Null"

        if exist src\\model\\train.py (
          "%VENV%\\Scripts\\python.exe" src\\model\\train.py || ( echo ERROR: training script failed & exit /b 3 )
        ) else (
          echo "No training script found; skipping training"
        )

        powershell -NoProfile -Command ^
          "try {
             $b = '%BUILD_DIR%';
             if (-not (Test-Path $b)) { New-Item -ItemType Directory -Force -Path $b | Out-Null }
             $paths = @();
             if (Test-Path 'src') { $paths += 'src' }
             if (Test-Path 'README.md') { $paths += 'README.md' }
             $dest = Join-Path -Path $b -ChildPath 'project.zip'
             if ($paths.Count -gt 0) { Compress-Archive -Path $paths -DestinationPath $dest -Force; Write-Host 'Created' $dest }
             else { 'placeholder' | Out-File -FilePath (Join-Path $b 'placeholder.txt'); Add-Type -AssemblyName System.IO.Compression.FileSystem; [IO.Compression.ZipFile]::CreateFromDirectory($b, $dest); Remove-Item (Join-Path $b 'placeholder.txt'); Write-Host 'Created placeholder' $dest }
           } catch { Write-Error 'Zipping failed: ' $_.Exception.Message; exit 4 }"

        echo "Build directory listing after artifact creation:"
        dir "%BUILD_DIR%" /A
        '''
      }
    }

    stage('Archive') {
      steps {
        archiveArtifacts artifacts: 'build/**', allowEmptyArchive: false
      }
    }

    stage('Persist locally (robocopy + fallback)') {
      steps {
        bat '''
        @echo off
        echo ==== COPY TO PERSISTENT DIR (robocopy with fallback) ====
        echo PERSISTENT_DIR=%PERSISTENT_DIR%

        REM Build destination path (include job/build)
        setlocal enabledelayedexpansion
        set DEST=%PERSISTENT_DIR%\\%JOB_NAME%\\%BUILD_NUMBER%_build\\build
        echo DEST=%DEST%

        REM Ensure persistent root and destination exist
        powershell -NoProfile -Command "New-Item -ItemType Directory -Force -Path '%PERSISTENT_DIR%' | Out-Null"
        powershell -NoProfile -Command "New-Item -ItemType Directory -Force -Path '%DEST%' | Out-Null"

        REM Quick write test - fail fast if service account can't write
        powershell -NoProfile -Command ^
          "try { [System.IO.File]::WriteAllText('%DEST%\\jenkins-write-test.txt', 'ok'); Write-Host 'WRITE_TEST_OK'; Remove-Item '%DEST%\\jenkins-write-test.txt' -ErrorAction SilentlyContinue } catch { Write-Error 'WRITE_TEST_FAIL: ' $_.Exception.Message; exit 6 }"
        if errorlevel 1 (
          echo ERROR: cannot write to persistent destination %DEST% - check permissions/drive
          exit /b 6
        ) else (
          echo WRITE_TEST_OK
        )

        REM Ensure build dir exists
        if not exist "%BUILD_DIR%" (
          echo ERROR: Build directory not found: %BUILD_DIR%
          exit /b 5
        )

        echo "Source build folder contents:"
        dir "%BUILD_DIR%" /A

        REM Use robocopy with /E to copy everything (safer than /MIR during debugging)
        robocopy "%BUILD_DIR%" "%DEST%" /E /COPY:DAT /R:3 /W:5 /NP /NFL /NDL
        set RC=%ERRORLEVEL%
        echo robocopy exit code: %RC%

        if %RC% GEQ 8 (
          echo WARNING: robocopy failed with code %RC% - attempting PowerShell fallback
          powershell -NoProfile -Command ^
            "try { Copy-Item -Path '%BUILD_DIR%\\*' -Destination '%DEST%' -Recurse -Force -ErrorAction Stop; Write-Host 'PS_COPY_OK' } catch { Write-Error 'PS_COPY_FAIL: ' $_.Exception.Message; exit 7 }"
          if errorlevel 1 (
            echo ERROR: fallback PowerShell copy failed - check permissions/paths
            exit /b 7
          ) else (
            echo PS_COPY_OK
          )
        ) else (
          echo ROBOCOPY_OK
        )

        echo "Destination listing:"
        dir "%DEST%" /A
        endlocal
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
