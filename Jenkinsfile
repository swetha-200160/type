pipeline {
  agent any

  environment {
    VENV = "${WORKSPACE}/venv"
    BUILD_DIR = "${WORKSPACE}/build"
    PERSISTENT_DIR = "C:/jenkins-artifacts"
  }

  stages {
    stage('Checkout') { steps { checkout scm } }

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
          if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"
          powershell -Command "Compress-Archive -Path src,README.md -DestinationPath '%BUILD_DIR%\\project.zip' -Force"
          echo Created artifact %BUILD_DIR%\\project.zip
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
}
