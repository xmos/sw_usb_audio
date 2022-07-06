@Library('xmos_jenkins_shared_library@v0.19.0') _

getApproval()

pipeline {
  agent none
  options {
    skipDefaultCheckout()
  }
  parameters {
      choice(name: 'TEST_LEVEL', choices: ['smoke', 'nightly', 'weekend'],
             description: 'The level of test coverage to run')
  }
  environment {
    REPO = 'sw_usb_audio'
    VIEW = getViewName(REPO)
  }
  stages {
    stage('Create release and build') {
      agent {
        label 'macOS && x86_64'
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
                //sh 'xmake -C app_usb_aud_xk_316_mc -j16'
 
                sh 'xmake -C app_usb_aud_xk_216_mc -j16 CONFIG=2i10o10xxxxxx'
                stash includes: 'app_usb_aud_xk_216_mc/bin/**/*.xe', name: 'xk_216_mc_bin', useDefaultExcludes: false

                //sh 'xmake -C app_usb_aud_xk_evk_xu316 -j16 TEST_CONFIGS=1'
                //stash includes: 'app_usb_aud_xk_evk_xu316/bin/**/*.xe', name: 'xk_evk_xu316_bin', useDefaultExcludes: false

                //dir("doc") {
                //  sh 'xdoc xmospdf'
                //  dir("_build/xlatex") {
                //    archiveArtifacts artifacts: "index.pdf", fingerprint: true, allowEmptyArchive: true
                //  }
                //}
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
          cleanWs()
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
              copyArtifacts filter: 'host_xscope_controller/bin_macos/xscope_controller', fingerprintArtifacts: true, projectName: 'xmos-int/sw_audio_analyzer/master', selector: lastSuccessful()
            }
            dir("${REPO}") {
              unstash 'xk_216_mc_bin'
              //unstash 'xk_evk_xu316_bin'
              dir("tests") {
                // Build test support application
                sh 'make -C tools/volcontrol'

                dir("tools") {
                  copyArtifacts filter: 'bin_macos/xsig', fingerprintArtifacts: true, projectName: 'xmos-int/xsig/master', flatten: true, selector: lastSuccessful()
                }

                viewEnv() {
                  // The JENKINS env var is necessary for macOS catalina
                  // We have to work around microphone permission issues
                  // For more info, see the DevOps section of the XMOS wiki
                  withEnv(["JENKINS=1"]) {
                    withVenv() {
                      //sh "pytest -s -m ${params.TEST_LEVEL} -k analogue_input --junitxml=pytest_result.xml"
                      sh "xrun --adapter-id RdZ15gCf ${WORKSPACE}/sw_usb_audio/app_usb_aud_xk_216_mc/bin/2i10o10xxxxxx/app_usb_aud_xk_216_mc_2i10o10xxxxxx.xe"
                      sh "xrun --adapter-id WV22B7qE ${WORKSPACE}/sw_audio_analyzer/app_audio_analyzer_xcore200_mc/bin/app_audio_analyzer_xcore200_mc.xe"
                      sh "sleep 5"
                      sh "./tools/xsig 48000 10000 xsig_configs/mc_analogue_input_8ch.json"
                    }
                  }
                }
              }
            }
          }
        }
      }
      post {
        cleanup {
          cleanWs()
        }
      }
    }
    stage('Update view files') {
      agent {
        label 'linux && x86_64'
      }
      steps {
        updateViewfiles()
      }
    }
  }
}
