pipeline {
  agent any
  environment {
    VENV = "${WORKSPACE}\\venv"
    BUILD_DIR = "${WORKSPACE}\\build"
    PERSISTENT_DIR = "C:\\jenkins-artifacts"   // change to existing path
  }
  stages {
    stage('Checkout') { steps { checkout scm } }
    stage('Create venv') {
      steps {
        bat '''
        @echo off
        py -3 -m venv "%VENV%" || python -m venv "%VENV%"
        "%VENV%\\Scripts\\python.exe" -m pip install --upgrade pip
        if exist requirements.txt "%VENV%\\Scripts\\pip.exe" install -r requirements.txt
        '''
      }
    }
    stage('Train & Build') {
      steps {
        bat '''
        @echo off
        if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"
        "%VENV%\\Scripts\\python.exe" src\\model\\train.py || echo training failed
        if exist build.bat (
          call build.bat
        ) else (
          powershell -Command "Compress-Archive -Path src,README.md -DestinationPath '%BUILD_DIR%\\project.zip' -Force"
        )
        dir "%BUILD_DIR%"
        '''
      }
    }
    stage('Archive') {
      steps { archiveArtifacts artifacts: 'build\\\\**', allowEmptyArchive: true }
    }
    stage('Persist locally') {
      steps {
        bat '''
        @echo off
        if not exist "%PERSISTENT_DIR%\\%JOB_NAME%" mkdir "%PERSISTENT_DIR%\\%JOB_NAME%"
        xcopy "%BUILD_DIR%" "%PERSISTENT_DIR%\\%JOB_NAME%\\%BUILD_NUMBER%_build\\build" /E /I /Y
        echo Copied build to %PERSISTENT_DIR%\\%JOB_NAME%\\%BUILD_NUMBER%_build
        '''
      }
    }
  }
  post {
    success { echo "Pipeline succeeded" }
  }
}
