@Library('xmos_jenkins_shared_library@v0.15.0') _

getApproval()

pipeline {
  agent none
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
        //stage('Create release') {
        //  // This stage has to happen before everything else! It requires a clean
        //  // sandbox
        //  steps {
        //    dir("${REPO}") {
        //      viewEnv() {
        //        runPython("python create_release.py --view ${VIEW}")
        //      }
        //    }
        //  }
        //}
        stage('Build') {
          steps {
            // We should pull the audio analyzer bin in as a binary dependency
            // Rather than build here
            dir("${WORKSPACE}/sw_audio_analyzer/app_audio_analyzer_xcore200_mc") {
              viewEnv() {
                runXmake(".")
              }
            }
            dir("${WORKSPACE}") {
                stash includes: 'sw_audio_analyzer/app_audio_analyzer_xcore200_mc/bin/**/*', name: 'audio_analyzer_bin', useDefaultExcludes: false
            }
            dir("${REPO}/tests") {
              viewEnv() {
                // Build all firmware but don't run any tests
                runPytest('--numprocesses=1 --build-only')
              }
            }
            dir("${REPO}") {
              stash includes: 'app_usb_aud_xk_216_mc/bin/**/*', name: 'xk_216_mc_bin', useDefaultExcludes: false
            }
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
    stage('Regression Test') {
      agent {
        label 'usb_audio'
      }
      stages {
        stage('Get view') {
          steps {
            xcorePrepareSandbox("${VIEW}", "${REPO}")
          }
        }
        stage('Test') {
          steps {
            dir("${WORKSPACE}") {
              unstash 'audio_analyzer_bin'
            }
            dir("${REPO}") {
              unstash 'xk_216_mc_bin'
              dir("tests") {
                viewEnv() {
                  runPytest('--numprocesses=1 --test-only')
                }
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
}
