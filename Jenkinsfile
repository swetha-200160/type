pipeline {
    agent any

    environment {
        BUILD_OUTPUT = "C:\\Users\\swethasuresh\\testing"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'master',
                    credentialsId: 'gitrepo',
                    url: 'https://github.com/swetha-200160/type.git'
            }
        }

        stage('Build') {
            steps {
                echo 'Building Python project...'
                bat '''
@echo off
echo ==== PYTHON BUILD START ====
setlocal

if not exist "venv\\Scripts\\python.exe" (
    py -3 -m venv venv
)
call "venv\\Scripts\\activate"

python -m pip install --upgrade pip

if exist "requirements.txt" (
    pip install -r "requirements.txt"
) else (
    pip install scikit-learn joblib
)

if exist "%WORKSPACE%\\train.py" (
    echo Running "%WORKSPACE%\\train.py"
    python "%WORKSPACE%\\train.py"
) else (
    if exist "C:\\ProgramData\\python pjt\\src\\model\\train.py" (
        echo Running "C:\\ProgramData\\python pjt\\src\\model\\train.py"
        python "C:\\ProgramData\\python pjt\\src\\model\\train.py"
    ) else (
        echo No train.py found in workspace or alternate path
        exit /b 0
    )
)

endlocal
echo ==== PYTHON BUILD END ====
'''
            }
        }

        stage('Gather Artifacts') {
            steps {
                script {
                    bat """
@echo off
set ARTIFACT_DIR=%WORKSPACE%\\build_artifacts

if exist "%ARTIFACT_DIR%" rmdir /S /Q "%ARTIFACT_DIR%"
mkdir "%ARTIFACT_DIR%"

REM copy model file if present
if exist "%WORKSPACE%\\src\\model\\model.pkl" (
  copy "%WORKSPACE%\\src\\model\\model.pkl" "%ARTIFACT_DIR%\\" >nul
)

REM copy entire model folder
if exist "%WORKSPACE%\\src\\model" (
  xcopy "%WORKSPACE%\\src\\model\\" "%ARTIFACT_DIR%\\model\\" /E /I /Y >nul
)

REM copy dist folder
if exist "%WORKSPACE%\\dist" (
  xcopy "%WORKSPACE%\\dist\\" "%ARTIFACT_DIR%\\dist\\" /E /I /Y >nul
)

REM copy other useful files
if exist "%WORKSPACE%\\requirements.txt" copy "%WORKSPACE%\\requirements.txt" "%ARTIFACT_DIR%\\" >nul
if exist "%WORKSPACE%\\train.log" copy "%WORKSPACE%\\train.log" "%ARTIFACT_DIR%\\" >nul

echo Artifacts prepared under %ARTIFACT_DIR%
echo ===== Source artifact listing (size bytes) =====
for /R "%ARTIFACT_DIR%" %%F in (*) do @echo %%~zF bytes - %%~fF
echo ===== Source artifact MD5 hashes =====
for /R "%ARTIFACT_DIR%" %%F in (*) do @echo --- %%~fF --- & certutil -hashfile "%%~fF" MD5
"""
                }
            }
        }

        stage('Copy Artifacts to Target') {
            steps {
                script {
                    bat """
@echo off
set ARTIFACT_DIR=%WORKSPACE%\\build_artifacts
set TARGET=%BUILD_OUTPUT%

if not exist "%TARGET%" mkdir "%TARGET%"

echo Starting robocopy from "%ARTIFACT_DIR%" to "%TARGET%"
robocopy "%ARTIFACT_DIR%" "%TARGET%" /E /XO /R:2 /W:2 /NFL /NDL

set RC=%ERRORLEVEL%
echo Robocopy exit code: %RC%
if %RC% LEQ 7 (
  echo Robocopy finished with acceptable code %RC%.
) else (
  echo Robocopy FAILED with code %RC%.
  exit /b %RC%
)
"""
                }
            }
        }

        stage('Verify Target Artifacts') {
            steps {
                script {
                    bat """
@echo off
set ARTIFACT_DIR=%WORKSPACE%\\build_artifacts
set TARGET=%BUILD_OUTPUT%

echo ===== Target artifact listing (size bytes) =====
for /R "%TARGET%" %%F in (*) do @echo %%~zF bytes - %%~fF

echo ===== Compare sizes and hashes =====
set FAIL=0

for /R "%ARTIFACT_DIR%" %%S in (*) do (
  set "SRC=%%~fS"
  setlocal enabledelayedexpansion
  REM derive relative path from ARTIFACT_DIR
  set "REL=!SRC:%ARTIFACT_DIR%\\=!"
  endlocal & set "REL=%REL%"

  set "DST=%TARGET%\\%REL%"

  if not exist "%DST%" (
    echo MISSING: "%DST%"
    set FAIL=1
  ) else (
    REM get sizes
    for %%A in ("%%~fS") do set "SZ_SRC=%%~zA"
    for %%B in ("%DST%") do set "SZ_DST=%%~zB"
    if not "!SZ_SRC!"=="!SZ_DST!" (
      echo SIZE_MISMATCH: Source=%%~fS (!SZ_SRC!) Target=%DST% (!SZ_DST!)
      set FAIL=1
    ) else (
      REM compare MD5
      for /f "tokens=1*" %%H in ('certutil -hashfile "%%~fS" MD5 ^| findstr /v /c:"CertUtil" /c:"MD5"') do set "HASH_SRC=%%H %%I"
      for /f "tokens=1*" %%H in ('certutil -hashfile "%DST%" MD5 ^| findstr /v /c:"CertUtil" /c:"MD5"') do set "HASH_DST=%%H %%I"
      if not "%HASH_SRC%"=="%HASH_DST%" (
        echo HASH_MISMATCH: "%%~fS"
        echo   src=%HASH_SRC%
        echo   dst=%HASH_DST%
        set FAIL=1
      ) else (
        echo OK: "%%~fS" -> "%DST%" (size !SZ_SRC!)
      )
    )
  )
)

if "%FAIL%"=="1" (
  echo ONE OR MORE ARTIFACTS FAILED VERIFICATION.
  exit /b 2
) else (
  echo All artifacts verified OK.
)
"""
                }
            }
        }

        stage('Archive Artifacts (Jenkins)') {
            steps {
                archiveArtifacts artifacts: 'build_artifacts/**', fingerprint: true
            }
        }
    }

    post {
        success {
            echo 'Build completed successfully and artifacts copied & verified'
        }
        failure {
            echo 'Build failed or verification failed. Check console output for details.'
        }
    }
}
