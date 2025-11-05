pipeline {
    agent any

    environment {
        BUILD_OUTPUT = "C:\ProgramData\python pjt"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    credentialsId: 'gitrepo',
                    url: 'https://github.com/swetha-200160/type.git'
            }
        }

        stage('Build') {
            steps {
                echo 'Building Java project...'
                bat 'mvn clean package -DskipTests'
            }
        }

        stage('Copy Build Files (all workspace - robocopy)') {
            steps {
                script {
                    echo "Copying entire workspace to ${env.BUILD_OUTPUT} (preserving folders)"
                    bat """
                    REM ensure destination exists
                    if not exist "${env.BUILD_OUTPUT}" mkdir "${env.BUILD_OUTPUT}"

                    REM use robocopy to copy current workspace to destination, exclude .git
                    robocopy "%CD%" "${env.BUILD_OUTPUT}" /E /XO /R:2 /W:2 /XD ".git" /NFL /NDL

                    REM capture robocopy exit code
                    set RC=%ERRORLEVEL%
                    echo Robocopy exit code: %RC%

                    REM treat 0-7 as success, >7 as failure
                    if %RC% LEQ 7 (
                      echo Robocopy finished with acceptable code %RC%. Exiting success.
                      exit /b 0
                    )

                    echo Robocopy FAILED with code %RC%. Exiting with failure.
                    exit /b %RC%
                    """
                }
            }
        }
    }

    post {
        success {
            echo 'Build completed successfully and entire workspace copied to target folder'
        }
        failure {
            echo 'Build or copy failed!'
        }
    }
}