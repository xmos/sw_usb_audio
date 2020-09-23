@Library('xmos_jenkins_shared_library@v0.14.1') _

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
    VIEW = 'usb_audio_stable'
  }
  stages {
    stage('Create release and build') {
      agent {
        label 'macOS&&x86_64&&brew'
      }
      stages {
        stage('Get view') {
          steps {
            xcorePrepareSandbox("${VIEW}", "${REPO}")
          }
        }
        stage('Create release') {
          // This stage has to happen before everything else! It requires a clean
          // sandbox
          steps {
            dir("${REPO}") {
              viewEnv() {
                runPython("python create_release.py --view ${VIEW}")
              }
            }
          }
        }
        stage('Build') {
          steps {
            dir("${REPO}/app_usb_aud_xk_216_mc") {
              viewEnv() {
                runXmake(".")
                sh "mv bin xk_216_mc_bin"
                stash includes: 'xk_216_mc_bin/**/*', name: 'xk_216_mc_bin', useDefaultExcludes: false
              }
            }
          }
        }
      }
      post {
        cleanup {
          xcoreCleanSandbox()
        }
      }
    }
    stage('Regression Test') {
      agent {
        label 'usb_audio_hw_linux'
      }
      stages {
        stage('Get view') {
          steps {
            xcorePrepareSandbox("${VIEW}", "${REPO}")
          }
        }
        stage('Test') {
          steps {
            dir("${REPO}/tests") {
              viewEnv() {
                unstash 'xk_216_mc_bin'
                runPytest('--numprocesses=1')
              }
            }
          }
        }
      }
      post {
        cleanup {
          xcoreCleanSandbox()
        }
      }
    }
    stage('Update view files') {
      agent {
        label 'x86_64'
      }
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
