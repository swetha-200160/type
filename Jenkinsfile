pipeline {
  agent any

  environment {
    BUILD_OUTPUT = "C:\\Users\\swethasuresh\\testing"
    // Comma-separated list of folders (relative to workspace) that you want copied into the build files.
    // Edit this value to include the exact folder names you want (examples: build,src,dist,reports)
    FOLDERS_TO_COPY = "build,src,dist,reports"
  }

  stages {
    stage('Checkout') {
      steps {
        git branch: 'master',
            credentialsId: 'gitrepo',
            url: 'https://github.com/swetha-200160/type.git'
      }
    }

    stage('Build (run training if any)') {
      steps {
        echo 'Running build/train (if present)...'
        bat '''
@echo off
echo ==== BUILD / TRAIN STAGE ====

if exist "%WORKSPACE%\\train.py" (
  echo Running "%WORKSPACE%\\train.py"
  python "%WORKSPACE%\\train.py"
) else (
  echo No train.py in workspace (skipping)
)

echo ==== BUILD / TRAIN DONE ====
'''
      }
    }

    stage('Prepare build_artifacts (copy selected folders)') {
      steps {
        script {
          // Use PowerShell inside a bat block to copy folder list robustly
          bat """
powershell -NoProfile -Command ^
  $folders = '${env.FOLDERS_TO_COPY}' -split ',' | ForEach-Object { $_.Trim() } ; ^
  $ws = $env:WORKSPACE ; ^
  $art = Join-Path $ws 'build_artifacts' ; ^
  if (Test-Path $art) { Remove-Item -Recurse -Force $art } ; ^
  New-Item -ItemType Directory -Force -Path $art | Out-Null ; ^
  foreach ($f in $folders) { ^
    if ([string]::IsNullOrWhiteSpace($f)) { continue } ^
    $src = Join-Path $ws $f ; ^
    if (Test-Path $src) { ^
      Write-Output \"Copying folder: $src -> $art\\$f\" ; ^
      $dst = Join-Path $art $f ; ^
      Copy-Item -Path $src -Destination $dst -Recurse -Force ; ^
    } else { Write-Output \"Folder not present, skipping: $src\" } ^
  } ; ^
  Write-Output \"`nPrepared build_artifacts contents:\" ; ^
  Get-ChildItem -Recurse -File $art | ForEach-Object { Write-Output (\"{0} {1}\" -f $_.Length, $_.FullName) }
"""
        }
      }
    }

    stage('Copy build_artifacts to BUILD_OUTPUT and verify') {
      steps {
        bat '''
powershell -NoProfile -Command ^
  $src = Join-Path $env:WORKSPACE 'build_artifacts'; ^
  $dst = $env:BUILD_OUTPUT; ^
  if (-not (Test-Path $src)) { Write-Error "No artifacts to copy: $src"; exit 2 } ; ^
  if (-not (Test-Path $dst)) { New-Item -ItemType Directory -Force -Path $dst | Out-Null } ; ^
  Write-Output "Copying artifacts from $src to $dst"; ^
  Get-ChildItem -Recurse -File $src | ForEach-Object { ^
    $rel = $_.FullName.Substring($src.Length + 1); ^
    $target = Join-Path $dst $rel; ^
    $tDir = Split-Path $target -Parent; ^
    if (-not (Test-Path $tDir)) { New-Item -ItemType Directory -Force -Path $tDir | Out-Null } ^
    Copy-Item -Path $_.FullName -Destination $target -Force ; ^
  } ; ^
  Write-Output "`nTarget listing (size bytes):"; ^
  Get-ChildItem -Recurse -File $dst | ForEach-Object { Write-Output (\"{0} {1}\" -f $_.Length, $_.FullName) } ; ^
  Write-Output "`nVerifying MD5 (source -> target)"; ^
  $fail = $false; ^
  Get-ChildItem -Recurse -File $src | ForEach-Object { ^
    $srcFile = $_.FullName; ^
    $rel = $srcFile.Substring($src.Length + 1); ^
    $tgtFile = Join-Path $dst $rel; ^
    if (-not (Test-Path $tgtFile)) { Write-Error \"MISSING target: $tgtFile\"; $fail = $true; return } ^
    if ((Get-Item $srcFile).Length -eq 0) { Write-Error \"ZERO-SIZE SOURCE: $srcFile\"; $fail = $true; return } ^
    if ((Get-Item $srcFile).Length -ne (Get-Item $tgtFile).Length) { Write-Error \"SIZE MISMATCH: $srcFile != $tgtFile\"; $fail = $true; return } ^
    $hSrc = (certutil -hashfile $srcFile MD5) -join \"`n\" ; $hTgt = (certutil -hashfile $tgtFile MD5) -join \"`n\" ; ^
    if ($hSrc -ne $hTgt) { Write-Error \"HASH MISMATCH: $srcFile\"; $fail = $true; return } ^
  } ; ^
  if ($fail) { Write-Error 'Artifact verification failed'; exit 3 } else { Write-Output 'All artifacts copied and verified OK' }
'''
      }
    }

    stage('Archive') {
      steps {
        archiveArtifacts artifacts: 'build_artifacts/**', fingerprint: true
      }
    }
  }

  post {
    success {
      echo 'Folders copied to BUILD_OUTPUT and archived successfully.'
    }
    failure {
      echo 'Copy or verification failed — check console for details.'
    }
  }
}
