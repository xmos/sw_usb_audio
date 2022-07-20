@Library('xmos_jenkins_shared_library@v0.19.0') _

def withXTAG(List targets, Closure body) {
  def xtagIds = []

  try {
    targets.each {
      def adapterId = sh (script: "xtagctl acquire ${it}", returnStdout: true).trim()
      xtagIds.add(adapterId)
    }
    body(xtagIds)
  } finally {
    xtagIds.each {
      sh "xtagctl release ${it}"
    }
  }
}

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
        label '(linux || macOS) && x86_64'
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
                sh 'xmake -C app_usb_aud_xk_316_mc -j16 TEST_CONFIGS=1'
                stash includes: 'app_usb_aud_xk_316_mc/bin/**/*.xe', name: 'xk_316_mc_bin', useDefaultExcludes: false
 
                sh 'xmake -C app_usb_aud_xk_216_mc -j16 TEST_CONFIGS=1'
                stash includes: 'app_usb_aud_xk_216_mc/bin/**/*.xe', name: 'xk_216_mc_bin', useDefaultExcludes: false

                sh 'xmake -C app_usb_aud_xk_evk_xu316 -j16 TEST_CONFIGS=1'
                stash includes: 'app_usb_aud_xk_evk_xu316/bin/**/*.xe', name: 'xk_evk_xu316_bin', useDefaultExcludes: false

                dir("doc") {
                  sh 'xdoc xmospdf'
                  dir("_build/xlatex") {
                    archiveArtifacts artifacts: "index.pdf", fingerprint: true, allowEmptyArchive: true
                  }
                }
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
      parallel {
        stage('MacOS Intel') {
          agent {
            label 'usb_audio && macos && x86_64 && xcore200-mcab && xcore.ai-explorer'
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
                  unstash 'xk_evk_xu316_bin'
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
                          sh "pip install -e ${WORKSPACE}/xtagctl"
                          withXTAG(["usb_audio_mc_xs2_dut", "usb_audio_mc_xs2_harness", \
                                    "usb_audio_xcai_exp_dut", "usb_audio_xcai_exp_harness"]) { xtagIds ->
                            sh "pytest -m ${params.TEST_LEVEL} --junitxml=pytest_result.xml \
                                -o xk_216_mc_dut=${xtagIds[0]} -o xk_216_mc_harness=${xtagIds[1]} \
                                -o xk_evk_xu316_dut=${xtagIds[2]} -o xk_evk_xu316_harness=${xtagIds[3]}"
                          }
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
        stage('MacOS ARM') {
          agent {
            label 'usb_audio && macos && arm64 && xcore.ai-mcab'
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
                  unstash 'xk_316_mc_bin'
                  dir("tests") {
                    // Build test support application
                    sh 'make -C tools/volcontrol'

                    dir("tools") {
                      copyArtifacts filter: 'bin_macos_m1/xsig', fingerprintArtifacts: true, projectName: 'xmos-int/xsig/master', flatten: true, selector: lastSuccessful()
                    }

                    viewEnv() {
                      // The JENKINS env var is necessary for macOS catalina
                      // We have to work around microphone permission issues
                      // For more info, see the DevOps section of the XMOS wiki
                      withEnv(["JENKINS=1"]) {
                        withVenv() {
                          sh "pip install -e ${WORKSPACE}/xtagctl"
                          withXTAG(["usb_audio_mc_xcai_dut", "usb_audio_mc_xcai_harness"]) { xtagIds ->
                            sh "pytest -m ${params.TEST_LEVEL} --junitxml=pytest_result.xml \
                                -o xk_316_mc_dut=${xtagIds[0]} -o xk_316_mc_harness=${xtagIds[1]}"
                          }
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
