@Library('xmos_jenkins_shared_library@v0.15.0') _

getApproval()

pipeline {
  agent none
  options {
    skipDefaultCheckout()
  }
  environment {
    REPO = 'sw_usb_audio'
    VIEW = getViewName(REPO)
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
            viewEnv() {
              dir("${REPO}") {
                sh 'xmake -C app_usb_aud_xk_216_mc -j16 TEST_CONFIGS=1'
                stash includes: 'app_usb_aud_xk_216_mc/bin/**/*.xe', name: 'xk_216_mc_bin', useDefaultExcludes: false
                sh 'xmake -C app_usb_aud_xk_evk_xu316 -j16 TEST_CONFIGS=1'
              }
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
            dir("${WORKSPACE}/sw_audio_analyzer") {
              copyArtifacts filter: '**/*.xe', fingerprintArtifacts: true, projectName: 'xmos-int/sw_audio_analyzer/master', selector: lastSuccessful()
            }
            dir("${REPO}") {
              unstash 'xk_216_mc_bin'
              dir("tests") {
                viewEnv() {
                  // The JENKINS env var is necessary for macOS catalina
                  // We have to work around microphone permission issues
                  // For more info, see the DevOps section of the XMOS wiki
                  withEnv(["JENKINS=1"]) {
                    runPytest('--numprocesses=1')
                  }
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
