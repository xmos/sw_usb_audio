@Library('xmos_jenkins_shared_library@feature/west_support') _

getApproval()

pipeline {
  agent none
  options {
    skipDefaultCheckout()
    disableConcurrentBuilds()
  }
  parameters {
      choice(name: 'TEST_LEVEL', choices: ['smoke', 'nightly', 'weekend'],
             description: 'The level of test coverage to run')
      string(name: 'ROLL_DEPS_CMD', defaultValue: '',
             description: 'A git command that is run on all repos before the build to check them out to a version')
  }
  environment {
    REPO = 'sw_usb_audio'
    VIEW = getViewName(REPO)
  }
  stages {
    stage('Build') {
      agent {
        label '(linux || macOS) && x86_64'
      }
      stages {
        stage('Get view') {
          steps {
            xcorePrepareWestWorkspace(REPO, params.ROLL_DEPS_CMD)
          }
        }
        stage('Build applications') {
          steps {
            viewEnv() {
              dir("${REPO}") {
                // Build and archive the main app configs; doing each app separately is faster than xmake in top directory
                sh 'xmake -C app_usb_aud_xk_316_mc -j16'
                sh 'xmake -C app_usb_aud_xk_216_mc -j16'
                sh 'xmake -C app_usb_aud_xk_evk_xu316 -j16'
                archiveArtifacts artifacts: "app_usb_aud_*/bin/**/*.xe", fingerprint: true, allowEmptyArchive: false

                // Build all other configs for testing and stash for stages on the later agents
                sh 'xmake -C app_usb_aud_xk_316_mc -j16 BUILD_TEST_CONFIGS=1 TEST_SUPPORT_CONFIGS=1'
                stash includes: 'app_usb_aud_xk_316_mc/bin/**/*.xe', name: 'xk_316_mc_bin', useDefaultExcludes: false

                sh 'xmake -C app_usb_aud_xk_216_mc -j16 BUILD_TEST_CONFIGS=1 TEST_SUPPORT_CONFIGS=1'
                stash includes: 'app_usb_aud_xk_216_mc/bin/**/*.xe', name: 'xk_216_mc_bin', useDefaultExcludes: false

                sh 'xmake -C app_usb_aud_xk_evk_xu316 -j16 BUILD_TEST_CONFIGS=1 TEST_SUPPORT_CONFIGS=1'
                stash includes: 'app_usb_aud_xk_evk_xu316/bin/**/*.xe', name: 'xk_evk_xu316_bin', useDefaultExcludes: false

                // Build untested app
                sh 'xmake -C app_usb_aud_xk_evk_xu316_extrai2s -j16'
              }
            }
          }
        }
        stage('Build documentation') {
          steps {
            viewEnv() {
              dir("${REPO}/doc") {
                sh 'xdoc xmospdf'
                archiveArtifacts artifacts: "pdf/*.pdf", fingerprint: true, allowEmptyArchive: false
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
            stage('Setup') {
              steps {
                dir("${WORKSPACE}/sw_audio_analyzer") {
                  copyArtifacts filter: '**/*.xe', fingerprintArtifacts: true, projectName: 'xmos-int/sw_audio_analyzer/master', selector: lastSuccessful()
                  copyArtifacts filter: 'host_xscope_controller/bin_macos/xscope_controller', fingerprintArtifacts: true, projectName: 'xmos-int/sw_audio_analyzer/master', selector: lastSuccessful()
                }

                dir("${REPO}") {
                  unstash 'xk_216_mc_bin'
                  unstash 'xk_evk_xu316_bin'

                  dir("tests") {
                    withVenv() {
                      sh "pip install -e ${WORKSPACE}/xtagctl"
                    }

                    dir("tools") {
                      // Build test support application
                      sh 'make -C volcontrol'
                      copyArtifacts filter: 'bin-macos-x86/xsig', fingerprintArtifacts: true, projectName: 'xmos-int/xsig/master', flatten: true, selector: lastSuccessful()
                    }
                  }
                }
              }
            }
            stage('Test') {
              steps {
                dir("${REPO}/tests") {
                  viewEnv() {
                    withEnv(["USBA_MAC_PRIV_WORKAROUND=1"]) {
                      withVenv() {
                        withXTAG(["usb_audio_mc_xs2_dut", "usb_audio_mc_xs2_harness", \
                                  "usb_audio_xcai_exp_dut", "usb_audio_xcai_exp_harness"]) { xtagIds ->
                          sh "pytest -v --level ${params.TEST_LEVEL} --junitxml=pytest_result_mac_intel.xml \
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
          post {
            always {
              archiveArtifacts artifacts: "${REPO}/tests/pytest_result_mac_intel.xml", fingerprint: true, allowEmptyArchive: true
              junit "${REPO}/tests/pytest_result_mac_intel.xml"
            }
            cleanup {
              xcoreCleanSandbox()
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
            stage('Setup') {
              steps {
                dir("${WORKSPACE}/sw_audio_analyzer") {
                  copyArtifacts filter: '**/*.xe', fingerprintArtifacts: true, projectName: 'xmos-int/sw_audio_analyzer/master', selector: lastSuccessful()
                  copyArtifacts filter: 'host_xscope_controller/bin_macos/xscope_controller', fingerprintArtifacts: true, projectName: 'xmos-int/sw_audio_analyzer/master', selector: lastSuccessful()
                }

                dir("${REPO}") {
                  unstash 'xk_316_mc_bin'

                  dir("tests") {
                    withVenv() {
                      sh "pip install -e ${WORKSPACE}/xtagctl"
                    }

                    dir("tools") {
                      // Build test support application
                      sh 'make -C volcontrol'
                      copyArtifacts filter: 'bin-macos-arm/xsig', fingerprintArtifacts: true, projectName: 'xmos-int/xsig/master', flatten: true, selector: lastSuccessful()
                    }
                  }
                }
              }
            }
            stage('Test') {
              steps {
                dir("${REPO}/tests") {
                  viewEnv() {
                    withEnv(["USBA_MAC_PRIV_WORKAROUND=1"]) {
                      withVenv() {
                        withXTAG(["usb_audio_mc_xcai_dut", "usb_audio_mc_xcai_harness"]) { xtagIds ->
                          sh "pytest -v --level ${params.TEST_LEVEL} --junitxml=pytest_result_mac_arm.xml \
                              -o xk_316_mc_dut=${xtagIds[0]} -o xk_316_mc_harness=${xtagIds[1]}"
                        }
                      }
                    }
                  }
                }
              }
            }
          }
          post {
            always {
              archiveArtifacts artifacts: "${REPO}/tests/pytest_result_mac_arm.xml", fingerprint: true, allowEmptyArchive: true
              junit "${REPO}/tests/pytest_result_mac_arm.xml"
            }
            cleanup {
              xcoreCleanSandbox()
            }
          }
        }
        stage('Windows 10') {
          agent {
            label 'usb_audio && windows10 && xcore.ai-mcab'
          }
          stages {
            stage('Get view') {
              steps {
                xcorePrepareSandbox("${VIEW}", "${REPO}")
              }
            }
            stage('Setup') {
              steps {
                dir("${WORKSPACE}/sw_audio_analyzer") {
                  copyArtifacts filter: '**/*.xe', fingerprintArtifacts: true, projectName: 'xmos-int/sw_audio_analyzer/master', selector: lastSuccessful()
                }

                dir("${REPO}") {
                  unstash 'xk_316_mc_bin'

                  dir("tests") {
                    withVenv() {
                      dir("${WORKSPACE}/xtagctl") {
                        sh "pip install -e ."
                      }
                    }

                    dir("tools") {
                      copyArtifacts filter: 'bin-windows-x86/xsig.exe', fingerprintArtifacts: true, projectName: 'xmos-int/xsig/master', flatten: true, selector: lastSuccessful()
                    }
                  }
                }
              }
            }
            stage('Test') {
              steps {
                dir("${REPO}/tests") {
                  viewEnv() {
                    withVenv() {
                      withXTAG(["usb_audio_mc_xcai_dut", "usb_audio_mc_xcai_harness"]) { xtagIds ->
                        sh "pytest -v --level ${params.TEST_LEVEL} --junitxml=pytest_result_windows10.xml \
                            -o xk_316_mc_dut=${xtagIds[0]} -o xk_316_mc_harness=${xtagIds[1]}"
                      }
                    }
                  }
                }
              }
            }
          }
          post {
            always {
              archiveArtifacts artifacts: "${REPO}/tests/pytest_result_windows10.xml", fingerprint: true, allowEmptyArchive: true
              junit "${REPO}/tests/pytest_result_windows10.xml"
            }
            cleanup {
              xcoreCleanSandbox()
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
      post {
        cleanup {
          xcoreCleanSandbox()
        }
      }
    }
  }
}
