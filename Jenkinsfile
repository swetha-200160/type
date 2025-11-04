pipeline {
  agent any
  environment {
    VENV = "${WORKSPACE}\\C:\jenkins-artifacts\jenkins pipeline"
    BUILD_DIR = "${WORKSPACE}\\C:\jenkins-artifacts\jenkins pipeline"
    PERSISTENT_DIR = "D:\testproject\Html\jenkins-articrafts"   // change to existing path
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
        if not exist "C:\jenkins-artifacts\jenkins pipeline" mkdir "C:\jenkins-artifacts\jenkins pipeline"
        "%VENV%\\Scripts\\python.exe" src\\model\\train.py || echo training failed
        if exist build.bat (
          call build.bat
        ) else (
          powershell -Command "Compress-Archive -Path src,README.md -DestinationPath 'C:\jenkins-artifacts\jenkins pipeline' -Force"
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
        if not exist "D:\testproject\Html\jenkins-articrafts\\" mkdir "D:\testproject\Html\jenkins-articrafts\\"%JOB_NAME%"
        xcopy "D:\testproject\Html\jenkins-articrafts" "D:\testproject\Html\jenkins-articrafts\\%BUILD_NUMBER%_build\\build" /E /I /Y
        echo Copied build to D:\testproject\Html\jenkins-articrafts\\%JOB_NAME%\\%BUILD_NUMBER%_build
        '''
      }
    }
  }
  post {
    success { echo "Pipeline succeeded" }
  }
}
