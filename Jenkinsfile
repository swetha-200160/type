pipeline {
  agent any
  environment {
    VENV = "${WORKSPACE}/venv"
    BUILD_DIR = "${WORKSPACE}/build"
    PERSISTENT_DIR = "C:/jenkins-artifacts"
  }
  stages {
    stage('Checkout') { steps { checkout scm } }

    stage('Debug workspace') {
      steps {
        bat '''
        @echo off
        echo Workspace: %WORKSPACE%
        dir "%WORKSPACE%" /A
        powershell -Command "Get-ChildItem -Path '%WORKSPACE%' -Recurse | Select-Object FullName | Format-Table -AutoSize"
        '''
      }
    }

    stage('Create venv') {
      steps {
        bat '''
        @echo off
        py -3 -m venv "%VENV%"
        "%VENV%\\Scripts\\python.exe" -m pip install --upgrade pip
        echo Created venv at %VENV%
        '''
      }
    }

    stage('Build sample') {
      steps {
        bat '''
        @echo off
        setlocal
        if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"
        pushd "%WORKSPACE%"
        powershell -Command ^
          " $src = Test-Path -Path 'src'; $readme = Test-Path -Path 'README.md'; ^
            if (-not $src -and -not $readme) { Write-Error 'Neither src nor README.md found in workspace.'; exit 1 } ^
            ; $paths = @(); if ($src) { $paths += 'src' }; if ($readme) { $paths += 'README.md' }; ^
            Compress-Archive -Path $paths -DestinationPath (Join-Path '%BUILD_DIR%' 'project.zip') -Force; ^
            Write-Host 'Created artifact' (Join-Path '%BUILD_DIR%' 'project.zip') "
        set RC=%ERRORLEVEL%
        popd
        if %RC% neq 0 (
          echo "Compression failed with exit code %RC%"
          exit /b %RC%
        ) else (
          echo "Compression succeeded."
        )
        endlocal
        '''
      }
    }

    stage('Copy to persistent') {
      steps {
        bat '''
        @echo off
        if not exist "%PERSISTENT_DIR%" mkdir "%PERSISTENT_DIR%"
        xcopy "%BUILD_DIR%" "%PERSISTENT_DIR%\\%JOB_NAME%\\%BUILD_NUMBER%_build\\build" /E /I /Y
        echo Copied to %PERSISTENT_DIR%\\%JOB_NAME%\\%BUILD_NUMBER%_build
        '''
      }
    }
  }

  post {
    always { echo "Finished" }
  }
}
