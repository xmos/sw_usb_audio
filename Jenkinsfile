@Library('xmos_jenkins_shared_library@v0.13.0') _

getApproval()

pipeline {
  agent {
    label 'macOS&&x86_64&&brew'
  }
  options {
    skipDefaultCheckout()
  }
  environment {
    REPO = 'sw_usb_audio'
    VIEW = getViewName(REPO)
  }
  stages {
    stage('Get view') {
      steps {
        xcorePrepareSandbox("${VIEW}", "${REPO}")
      }
    }
    stage('Create release') {
      steps {
        dir("${REPO}") {
          viewEnv() {
            runPython("python create_release.py --view ${VIEW}")
          }
        }
      }
    }
    stage('Update view files') {
      steps {
        updateViewfiles()
      }
    }
  }
  post {
    always {
      archiveArtifacts artifacts: "Release/*.zip", fingerprint: true, allowEmptyArchive: true
    }
    cleanup {
      xcoreCleanSandbox()
    }
  }
}
