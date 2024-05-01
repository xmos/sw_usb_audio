@Library('xmos_jenkins_shared_library@v0.27.0') _

// Get XCommon CMake and log a record of the git commit
def get_xcommon_cmake() {
  sh "git clone -b develop git@github.com:xmos/xcommon_cmake"
  sh "git -C xcommon_cmake rev-parse HEAD"
}

getApproval()

pipeline {
  agent none
  options {
    skipDefaultCheckout()
    timestamps()
    buildDiscarder(xmosDiscardBuildSettings(onlyArtifacts=true))
  }
  parameters {
      choice(name: 'TEST_LEVEL', choices: ['smoke', 'nightly', 'weekend'],
             description: 'The level of test coverage to run')
  }
  environment {
    REPO = 'sw_usb_audio'
    VIEW = getViewName(REPO)
    TOOLS_VERSION = "15.2.1"
    XTAGCTL_VERSION = "v2.0.0"
  }
  stages {
    stage('Build') {
      parallel {
        stage('Build applications') {
          // Use XCommon CMake to fetch dependencies, but then build using legacy XCommon Makefiles
          agent {
           label 'linux && x86_64'
          }
          steps {
            println "Stage running on ${env.NODE_NAME}"
            get_xcommon_cmake()

            dir("${REPO}") {
              checkout scm

              withTools("${env.TOOLS_VERSION}") {
                withEnv(["XMOS_CMAKE_PATH=${WORKSPACE}/xcommon_cmake"]) {
                  // Fetch all dependencies using XCommon CMake
                  sh "cmake -G 'Unix Makefiles' -B build"

                  // Build the loopback version of the configs for 316 and rename them to have _i2sloopback
                  sh 'xmake -C app_usb_aud_xk_316_mc -j16 PARTIAL_TEST_CONFIGS=1 TEST_SUPPORT_CONFIGS=1 EXTRA_BUILD_FLAGS=-DI2S_LOOPBACK=1'
                  sh 'for folder in app_usb_aud_xk_316_mc/bin/?*; do mv "$folder" "${folder/%/_i2sloopback}"; done'
                  sh 'for config in app_usb_aud_xk_316_mc/bin/?*/*.xe; do mv "$config" "${config/%.xe/_i2sloopback.xe}"; done'

                  // xmake does not fully rebuild when different build parameters are given, so must be cleaned before building without loopback
                  sh 'xmake -C app_usb_aud_xk_316_mc -j16 PARTIAL_TEST_CONFIGS=1 TEST_SUPPORT_CONFIGS=1 clean'

                  // Build and archive the main app configs; doing each app separately is faster than xmake in top directory
                  sh 'xmake -C app_usb_aud_xk_316_mc -j16'
                  sh 'xmake -C app_usb_aud_xk_216_mc -j16'
                  sh 'xmake -C app_usb_aud_xk_evk_xu316 -j16'
                  archiveArtifacts artifacts: "app_usb_aud_*/bin/**/*.xe", excludes: "**/*_i2sloopback*" , fingerprint: true, allowEmptyArchive: false

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
          post {
            cleanup {
              xcoreCleanSandbox()
            }
          }
        }  // Build applications

        stage('(XCommon CMake) Build applications') {
          // Use XCommon CMake to fetch dependencies and build all application configs
          agent {
            label 'linux && x86_64'
          }
          steps {
            println "Stage running on ${env.NODE_NAME}"
            get_xcommon_cmake()

            dir("${REPO}") {
              checkout scm

              withTools("${env.TOOLS_VERSION}") {
                withEnv(["XMOS_CMAKE_PATH=${WORKSPACE}/xcommon_cmake"]) {
                  sh "cmake -G 'Unix Makefiles' -B build -D BUILD_TESTED_CONFIGS=TRUE"
                  sh "xmake -C build -j16"
                  archiveArtifacts artifacts: "build/manifest.txt", fingerprint: true, allowEmptyArchive: false
                }
              }
            }
          }
          post {
            cleanup {
              xcoreCleanSandbox()
            }
          }
        }  // (XCommon CMake) Build applications

        stage('Build documentation') {
          agent {
            label 'linux && x86_64'
          }
          steps {
            println "Stage running on ${env.NODE_NAME}"
            get_xcommon_cmake()

            // Temporary: get repos for xdoc until this project switches to xmosdoc
            sh "git clone -b swapps14 git@github.com:xmos/infr_scripts_pl"
            sh "git clone -b feature/update_xdoc_3_3_0 git@github0.xmos.com:xmos-int/xdoc_released"

            withAgentEnv() {
              sh """#!/bin/bash
                cd ${WORKSPACE}/infr_scripts_pl/Build
                source SetupEnv
                cd ${WORKSPACE}
                Build.pl VIEW=apps DOMAINS=xdoc_released
                """
            }

            dir("${REPO}") {
              checkout scm

              viewEnv {
                withTools("${env.TOOLS_VERSION}") {
                  withEnv(["XMOS_CMAKE_PATH=${WORKSPACE}/xcommon_cmake"]) {
                    sh "cmake -G 'Unix Makefiles' -B build"

                    dir("doc") {
                      sh 'xdoc xmospdf'
                      archiveArtifacts artifacts: "pdf/*.pdf", fingerprint: true, allowEmptyArchive: false
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
        }  // Build documentations
      }
    }  // Build

    stage('Regression Test') {
      parallel {
        stage('MacOS Intel') {
          agent {
            label 'usb_audio && macos && x86_64 && xcore200-mcab && xcore.ai-explorer'
          }
          steps {
            println "Stage running on ${env.NODE_NAME}"
            sh "git clone git@github0.xmos.com:xmos-int/xtagctl"
            sh "git -C xtagctl checkout ${env.XTAGCTL_VERSION}"

            dir("sw_audio_analyzer") {
              copyArtifacts filter: '**/*.xe', fingerprintArtifacts: true, projectName: 'xmos-int/sw_audio_analyzer/master', selector: lastSuccessful()
              copyArtifacts filter: 'host_xscope_controller/bin_macos/xscope_controller', fingerprintArtifacts: true, projectName: 'xmos-int/sw_audio_analyzer/master', selector: lastSuccessful()
            }

            dir("${REPO}") {
              checkout scm
              createVenv("requirements.txt")
              withVenv() {
                sh "pip install -r requirements.txt"
              }

              unstash 'xk_216_mc_bin'
              unstash 'xk_evk_xu316_bin'

              dir("tests") {
                dir("tools") {
                  // Build test support application
                  dir("volcontrol") {
                    sh 'cmake -B build'
                    sh 'make -C build'
                  }
                  copyArtifacts filter: 'bin-macos-x86/xsig', fingerprintArtifacts: true, projectName: 'xmos-int/xsig/master', flatten: true, selector: lastSuccessful()
                  copyArtifacts filter: 'OSX/x86/xmos_mixer', fingerprintArtifacts: true, projectName: 'XMOS/lib_xua/develop', flatten: true, selector: lastSuccessful()
                }

                withTools("${env.TOOLS_VERSION}") {
                  withEnv(["USBA_MAC_PRIV_WORKAROUND=1"]) {
                    withVenv() {
                      sh "pip install -e ${WORKSPACE}/xtagctl"

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
          post {
            always {
              archiveArtifacts artifacts: "${REPO}/tests/pytest_result_mac_intel.xml", fingerprint: true, allowEmptyArchive: true
              archiveArtifacts artifacts: "${REPO}/tests/tools/glitch.*.csv", fingerprint: true, allowEmptyArchive: true
              junit "${REPO}/tests/pytest_result_mac_intel.xml"
            }
            cleanup {
              xcoreCleanSandbox()
            }
          }
        }  // MacOS Intel

        stage('MacOS ARM') {
          agent {
            label 'usb_audio && macos && arm64 && xcore.ai-mcab'
          }
          steps {
            println "Stage running on ${env.NODE_NAME}"
            sh "git clone git@github0.xmos.com:xmos-int/xtagctl"
            sh "git -C xtagctl checkout ${env.XTAGCTL_VERSION}"

            dir("sw_audio_analyzer") {
              copyArtifacts filter: '**/*.xe', fingerprintArtifacts: true, projectName: 'xmos-int/sw_audio_analyzer/master', selector: lastSuccessful()
              copyArtifacts filter: 'host_xscope_controller/bin_macos/xscope_controller', fingerprintArtifacts: true, projectName: 'xmos-int/sw_audio_analyzer/master', selector: lastSuccessful()
            }

            dir("${REPO}") {
              checkout scm
              createVenv("requirements.txt")
              withVenv() {
                sh "pip install -r requirements.txt"
              }

              unstash 'xk_316_mc_bin'

              dir("tests") {
                dir("tools") {
                  // Build test support application
                  dir("volcontrol") {
                    sh 'cmake -B build'
                    sh 'make -C build'
                  }
                  copyArtifacts filter: 'bin-macos-arm/xsig', fingerprintArtifacts: true, projectName: 'xmos-int/xsig/master', flatten: true, selector: lastSuccessful()
                  copyArtifacts filter: 'OSX/x86/xmos_mixer', fingerprintArtifacts: true, projectName: 'XMOS/lib_xua/develop', flatten: true, selector: lastSuccessful()
                }

                withTools("${env.TOOLS_VERSION}") {
                  withEnv(["USBA_MAC_PRIV_WORKAROUND=1"]) {
                    withVenv() {
                      sh "pip install -e ${WORKSPACE}/xtagctl"

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
          post {
            always {
              archiveArtifacts artifacts: "${REPO}/tests/pytest_result_mac_arm.xml", fingerprint: true, allowEmptyArchive: true
              archiveArtifacts artifacts: "${REPO}/tests/tools/glitch.*.csv", fingerprint: true, allowEmptyArchive: true
              junit "${REPO}/tests/pytest_result_mac_arm.xml"
            }
            cleanup {
              xcoreCleanSandbox()
            }
          }
        }  // MacOS ARM

        stage('Windows 10') {
          agent {
            label 'usb_audio && windows10 && xcore.ai-mcab'
          }
          steps {
            println "Stage running on ${env.NODE_NAME}"
            sh "git clone git@github0.xmos.com:xmos-int/xtagctl"
            sh "git -C xtagctl checkout ${env.XTAGCTL_VERSION}"

            dir("sw_audio_analyzer") {
              copyArtifacts filter: '**/*.xe', fingerprintArtifacts: true, projectName: 'xmos-int/sw_audio_analyzer/master', selector: lastSuccessful()
              copyArtifacts filter: 'host_xscope_controller/bin_windows/xscope_controller.exe', fingerprintArtifacts: true, projectName: 'xmos-int/sw_audio_analyzer/master', selector: lastSuccessful()
            }

            dir("${REPO}") {
              checkout scm
              createVenv("requirements.txt")
              withVenv() {
                sh "pip install -r requirements.txt"
              }

              unstash 'xk_316_mc_bin'

              dir("tests") {
                dir("tools") {
                  dir("volcontrol") {
                    withVS() {
                      bat 'msbuild volcontrol.vcxproj /property:Configuration=Release /property:Platform=x64'
                    }
                  }
                  copyArtifacts filter: 'bin-windows-x86/xsig.exe', fingerprintArtifacts: true, projectName: 'xmos-int/xsig/master', flatten: true, selector: lastSuccessful()
                  copyArtifacts filter: 'Win/x64/xmos_mixer.exe', fingerprintArtifacts: true, projectName: 'XMOS/lib_xua/develop', flatten: true, selector: lastSuccessful()
                }

                withTools("${env.TOOLS_VERSION}") {
                  withVenv() {
                    dir("${WORKSPACE}/xtagctl") {
                      sh "pip install -e ."
                    }
                    withXTAG(["usb_audio_mc_xcai_dut", "usb_audio_mc_xcai_harness"]) { xtagIds ->
                      sh "pytest -v --level ${params.TEST_LEVEL} --junitxml=pytest_result_windows10.xml \
                          -o xk_316_mc_dut=${xtagIds[0]} -o xk_316_mc_harness=${xtagIds[1]}"
                    }
                  }
                }
              }
            }
          }
          post {
            always {
              archiveArtifacts artifacts: "${REPO}/tests/pytest_result_windows10.xml", fingerprint: true, allowEmptyArchive: true
              archiveArtifacts artifacts: "${REPO}/tests/tools/glitch.*.csv", fingerprint: true, allowEmptyArchive: true
              junit "${REPO}/tests/pytest_result_windows10.xml"
            }
            cleanup {
              xcoreCleanSandbox()
            }
          }
        }  // Windows 10

        stage('Windows 11') {
          agent {
            label 'usb_audio && windows11 && xcore.ai-mcab'
          }
          steps {
            println "Stage running on ${env.NODE_NAME}"
            sh "git clone git@github0.xmos.com:xmos-int/xtagctl"
            sh "git -C xtagctl checkout ${env.XTAGCTL_VERSION}"

            dir("sw_audio_analyzer") {
              copyArtifacts filter: '**/*.xe', fingerprintArtifacts: true, projectName: 'xmos-int/sw_audio_analyzer/master', selector: lastSuccessful()
              copyArtifacts filter: 'host_xscope_controller/bin_windows/xscope_controller.exe', fingerprintArtifacts: true, projectName: 'xmos-int/sw_audio_analyzer/master', selector: lastSuccessful()
            }

            dir("${REPO}") {
              checkout scm
              createVenv("requirements.txt")
              withVenv() {
                sh "pip install -r requirements.txt"
              }

              unstash 'xk_316_mc_bin'

              dir("tests") {
                dir("tools") {
                  dir("volcontrol") {
                    withVS() {
                      bat 'msbuild volcontrol.vcxproj /property:Configuration=Release /property:Platform=x64'
                    }
                  }
                  copyArtifacts filter: 'bin-windows-x86/xsig.exe', fingerprintArtifacts: true, projectName: 'xmos-int/xsig/master', flatten: true, selector: lastSuccessful()
                  copyArtifacts filter: 'Win/x64/xmos_mixer.exe', fingerprintArtifacts: true, projectName: 'XMOS/lib_xua/develop', flatten: true, selector: lastSuccessful()
                }

                withTools("${env.TOOLS_VERSION}") {
                  withVenv() {
                    dir("${WORKSPACE}/xtagctl") {
                      sh "pip install -e ."
                    }

                    withXTAG(["usb_audio_mc_xcai_dut", "usb_audio_mc_xcai_harness"]) { xtagIds ->
                      sh "pytest -v --level ${params.TEST_LEVEL} --junitxml=pytest_result_windows11.xml \
                          -o xk_316_mc_dut=${xtagIds[0]} -o xk_316_mc_harness=${xtagIds[1]}"
                    }
                  }
                }
              }
            }
          }
          post {
            always {
              archiveArtifacts artifacts: "${REPO}/tests/pytest_result_windows11.xml", fingerprint: true, allowEmptyArchive: true
              archiveArtifacts artifacts: "${REPO}/tests/tools/glitch.*.csv", fingerprint: true, allowEmptyArchive: true
              junit "${REPO}/tests/pytest_result_windows11.xml"
            }
            cleanup {
              xcoreCleanSandbox()
            }
          }
        }  // Windows 11
      }
    }  // Regression Test
  }
}
