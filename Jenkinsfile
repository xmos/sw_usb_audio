// This file relates to internal XMOS infrastructure and should be ignored by external users

@Library('xmos_jenkins_shared_library@v0.38.0') _

// Get XCommon CMake.
// This is required for compiling a factory image for a DFU test using tools 15.2.1
// to test DFU across XTC tools versions.
def get_xcommon_cmake() {
  sh "git clone -b v1.3.0 git@github.com:xmos/xcommon_cmake"
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

    string(
      name: 'XMOSDOC_VERSION',
      defaultValue: 'v7.2.0',
      description: 'The xmosdoc version')

    string(
      name: 'INFR_APPS_VERSION',
      defaultValue: 'v2.2.0',
      description: 'The infr_apps version'
    )
    string(
      name: 'TOOLS_VERSION',
      defaultValue: '15.3.1',
      description: 'The XTC tools version'
    )
  }
  environment {
    REPO = 'sw_usb_audio'
    VIEW = getViewName(REPO)
    PREV_TOOLS_VERSION = "15.2.1"
  }
  stages {
    stage('Build') {
      parallel {
        stage('(XCommon CMake) Build applications') {
          // Use XCommon CMake to fetch dependencies and build all application configs
          agent {
           label 'linux && x86_64'
          }
          steps {
            println "Stage running on ${env.NODE_NAME}"

            get_xcommon_cmake()

            dir("${REPO}") {
              checkoutScmShallow()

              withTools("${env.PREV_TOOLS_VERSION}") {
                withEnv(["XMOS_CMAKE_PATH=${WORKSPACE}/xcommon_cmake"]) {
                  // Build one of the configs with old XTC tools (15.2.1) for a DFU test which tests if an older tools version factory executable
                  // can download an upgrade image built with the latest tools.
                  dir("app_usb_aud_xk_316_mc") {
                    sh "cmake -G 'Unix Makefiles' -B build_old_tools"
                    sh "xmake -C build_old_tools -j16 1SMi2o2xxxxxx"
                    // Create binary file using the old tools xflash that can be written into the device using xflash --write-all during the test
                    sh "xflash bin/1SMi2o2xxxxxx/app_usb_aud_xk_316_mc_1SMi2o2xxxxxx.xe -o bin/1SMi2o2xxxxxx/app_usb_aud_xk_316_mc_1SMi2o2xxxxxx.bin"
                    // Move to a different directory so it doesn't get overwritten when the same config is compiled with the latest tools
                    sh 'mv bin/1SMi2o2xxxxxx bin/1SMi2o2xxxxxx_old_tools'
                    sh 'for config in bin/1SMi2o2xxxxxx_old_tools/*.bin; do mv "$config" "${config/%.bin/_old_tools.bin}"; done'
                    sh 'for config in bin/1SMi2o2xxxxxx_old_tools/*.xe; do mv "$config" "${config/%.xe/_old_tools.xe}"; done'
                    sh 'rm -rf build_old_tools'
                  }
                }
              }

              withTools(params.TOOLS_VERSION) {
                dir("tests") {
                  createVenv(reqFile: "requirements.txt")
                  withVenv() {
                    // Check that the app_configs_autogen.yml file is up to date
                    sh "python tools/app_configs_autogen/collect_configs.py check"
                    // Check that the BCD version in version.h matches the library version in settings.yml
                    sh "pytest -v test_version.py"
                  } // withVenv()
                } // dir("tests")
                // Build the loopback version of the configs for 316 and rename them to have _i2sloopback
                sh "cmake -S app_usb_aud_xk_316_mc/ -B build -DPARTIAL_TESTED_CONFIGS=1 -DEXTRA_BUILD_FLAGS='-DI2S_LOOPBACK=1'"
                sh "xmake -C build -j16"
                sh 'for folder in app_usb_aud_xk_316_mc/bin/?*; do if [[ ! $folder == *"old_tools"* ]] ; then mv "$folder" "${folder/%/_i2sloopback}"; fi ; done'
                sh 'for config in app_usb_aud_xk_316_mc/bin/?*/*.xe; do if [[ ! $config == *"old_tools"* ]] ; then mv "$config" "${config/%.xe/_i2sloopback.xe}"; fi ; done'

                sh 'rm -rf build'
                sh 'cmake -B build -DBUILD_TESTED_CONFIGS=1 -DTEST_SUPPORT_CONFIGS=1'
                sh 'xmake -C build -j16'

                stash includes: 'app_usb_aud_xk_316_mc/bin/**/*.xe, app_usb_aud_xk_316_mc/bin/**/*.bin', name: 'xk_316_mc_bin', useDefaultExcludes: false
                stash includes: 'app_usb_aud_xk_216_mc/bin/**/*.xe', name: 'xk_216_mc_bin', useDefaultExcludes: false
                stash includes: 'app_usb_aud_xk_evk_xu316/bin/**/*.xe', name: 'xk_evk_xu316_bin', useDefaultExcludes: false

                archiveArtifacts artifacts: "app_usb_aud_*/bin/**/*.xe", excludes: "**/*_i2sloopback*" , fingerprint: true, allowEmptyArchive: false
                archiveArtifacts artifacts: "build/manifest.txt", fingerprint: true, allowEmptyArchive: false

              }
            }
          }
          post {
            cleanup {
              xcoreCleanSandbox()
            }
          }
        }  // // (XCommon CMake) Build applications

        stage('legacy xmake build + build documentation + Library checks') {
          // Use XCommon CMake to fetch dependencies, but then build using legacy XCommon Makefiles
          agent {
            label 'linux && x86_64'
          }
          stages {
            stage('legacy xmake build')
            {
              steps {
                println "Stage running on ${env.NODE_NAME}"

                dir("${REPO}") {
                  checkoutScmShallow()

                  withTools(params.TOOLS_VERSION) {
                    // Fetch all dependencies using XCommon CMake
                    sh "cmake -G 'Unix Makefiles' -B build -DDEPS_CLONE_SHALLOW=TRUE"
                    sh 'xmake -C app_usb_aud_xk_316_mc -j16'
                    sh 'xmake -C app_usb_aud_xk_216_mc -j16'
                    sh 'xmake -C app_usb_aud_xk_evk_xu316 -j16'
                    sh 'xmake -C app_usb_aud_xk_evk_xu316_extrai2s -j16'
                  }
                }
              } // steps
            } // stage('legacy xmake build')

            stage('Library checks') {
              steps {
                withTools(params.TOOLS_VERSION) {
                  warnError("libchecks") {
                    runSwrefChecks("${WORKSPACE}/${REPO}", "${params.INFR_APPS_VERSION}")
                  } // warnError("libchecks")
                } // withTools(params.TOOLS_VERSION)
              } // steps
            } // stage('Library checks')
            stage('Build Documentation') {
              steps {
                dir("${REPO}") {
                  dir("tests") {
                    createVenv(reqFile: "requirements.txt")
                  } // dir("tests")
                  withVenv(venv_path="${WORKSPACE}/${REPO}/tests") {
                    warnError("Docs") {
                      buildDocs(xmosdocVenvPath: "${REPO}/tests")
                    }
                  } // withVenv
                } // dir("${REPO}")
              } // steps
            } // stage('Build Documentation')
            stage("Archive sandbox") {
              steps
              {
                archiveSandbox(REPO)
              }
            } // stage("Archive sandbox")
          } // stages
          post {
            cleanup {
              xcoreCleanSandbox()
            }
          } // post
        }  // stage('legacy xmake build + build documentation')
      } // parallel
    }  // stage('Build')

    stage('Regression Test') {
      parallel {
        stage('MacOS Intel') {
          agent {
            label 'usb_audio && macos && x86_64 && xcore200-mcab && xcore.ai-explorer'
          }
          steps {
            println "Stage running on ${env.NODE_NAME}"

            dir("sw_audio_analyzer") {
              copyArtifacts filter: '**/*.xe', fingerprintArtifacts: true, projectName: 'xmos-int/sw_audio_analyzer/master', selector: lastSuccessful()
              copyArtifacts filter: 'host_xscope_controller/bin_macos/xscope_controller', fingerprintArtifacts: true, projectName: 'xmos-int/sw_audio_analyzer/master', selector: lastSuccessful()
            }

            dir("${REPO}") {
              checkoutScmShallow()

              unstash 'xk_216_mc_bin'
              unstash 'xk_evk_xu316_bin'

              dir("tests") {
                createVenv(reqFile: "requirements.txt")
                dir("tools") {
                  copyArtifacts filter: 'OSX/x86/xmos_mixer', fingerprintArtifacts: true, projectName: 'XMOS/lib_xua/develop', flatten: true, selector: lastSuccessful()
                }

                withTools(params.TOOLS_VERSION) {
                  withEnv(["USBA_MAC_PRIV_WORKAROUND=1"]) {
                    withVenv() {
                      dir("${env.VIRTUAL_ENV}/src/hardware-test-tools") {
                        sh 'cmake -B build -G Ninja'
                        sh 'ninja -C build'

                        dir("xsig") {
                          copyArtifacts filter: 'bin-macos-x86/xsig', fingerprintArtifacts: true, projectName: 'xmos-int/xsig/master', flatten: true, selector: lastSuccessful()
                        }
                        dir("xmosdfu") {
                          copyArtifacts filter: 'OSX/x86/xmosdfu', fingerprintArtifacts: true, projectName: 'XMOS/lib_xua/develop', flatten: true, selector: lastSuccessful()
                        }
                      } // dir("${env.VIRTUAL_ENV}/src/hardware-test-tools")

                      withXTAG(["usb_audio_mc_xs2_dut", "usb_audio_mc_xs2_harness", \
                                "usb_audio_xcai_exp_dut", "usb_audio_xcai_exp_harness"]) { xtagIds ->
                        sh "pytest -v --level ${params.TEST_LEVEL} --junitxml=pytest_result_mac_intel.xml \
                            -o xk_216_mc_dut=${xtagIds[0]} -o xk_216_mc_harness=${xtagIds[1]} \
                            -o xk_evk_xu316_dut=${xtagIds[2]} -o xk_evk_xu316_harness=${xtagIds[3]}"
                      }
                      archiveArtifacts artifacts: "${env.VIRTUAL_ENV}/src/hardware-test-tools/xsig/glitch.*.csv", fingerprint: true, allowEmptyArchive: true
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
        }  // MacOS Intel

        stage('MacOS ARM') {
          agent {
            label 'usb_audio && macos && arm64 && xcore.ai-mcab'
          }
          steps {
            println "Stage running on ${env.NODE_NAME}"

            dir("sw_audio_analyzer") {
              copyArtifacts filter: '**/*.xe', fingerprintArtifacts: true, projectName: 'xmos-int/sw_audio_analyzer/master', selector: lastSuccessful()
              copyArtifacts filter: 'host_xscope_controller/bin_macos/xscope_controller', fingerprintArtifacts: true, projectName: 'xmos-int/sw_audio_analyzer/master', selector: lastSuccessful()
            }

            dir("${REPO}") {
              checkoutScmShallow()

              unstash 'xk_316_mc_bin'

              dir("tests") {
                createVenv(reqFile: "requirements.txt")
                dir("tools") {
                  copyArtifacts filter: 'OSX/x86/xmos_mixer', fingerprintArtifacts: true, projectName: 'XMOS/lib_xua/develop', flatten: true, selector: lastSuccessful()
                }

                withTools(params.TOOLS_VERSION) {
                  withEnv(["USBA_MAC_PRIV_WORKAROUND=1"]) {
                    withVenv() {
                      dir("${env.VIRTUAL_ENV}/src/hardware-test-tools") {
                        sh 'cmake -B build -G Ninja'
                        sh 'ninja -C build'

                        dir("xsig") {
                          copyArtifacts filter: 'bin-macos-arm/xsig', fingerprintArtifacts: true, projectName: 'xmos-int/xsig/master', flatten: true, selector: lastSuccessful()
                        }
                        dir("xmosdfu") {
                          copyArtifacts filter: 'OSX/arm64/xmosdfu', fingerprintArtifacts: true, projectName: 'XMOS/lib_xua/develop', flatten: true, selector: lastSuccessful()
                        }
                      } // dir("${env.VIRTUAL_ENV}/src/hardware-test-tools")

                      withXTAG(["usb_audio_mc_xcai_dut", "usb_audio_mc_xcai_harness"]) { xtagIds ->
                        sh "pytest -v --level ${params.TEST_LEVEL} --junitxml=pytest_result_mac_arm.xml \
                            -o xk_316_mc_dut=${xtagIds[0]} -o xk_316_mc_harness=${xtagIds[1]} "
                      }
                      archiveArtifacts artifacts: "${env.VIRTUAL_ENV}/src/hardware-test-tools/xsig/glitch.*.csv", fingerprint: true, allowEmptyArchive: true
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
        }  // MacOS ARM

        stage('Windows 10') {
          agent {
            label 'usb_audio && windows10 && xcore.ai-mcab'
          }
          steps {
            println "Stage running on ${env.NODE_NAME}"

            dir("sw_audio_analyzer") {
              copyArtifacts filter: '**/*.xe', fingerprintArtifacts: true, projectName: 'xmos-int/sw_audio_analyzer/master', selector: lastSuccessful()
              copyArtifacts filter: 'host_xscope_controller/bin_windows/xscope_controller.exe', fingerprintArtifacts: true, projectName: 'xmos-int/sw_audio_analyzer/master', selector: lastSuccessful()
            }

            dir("${REPO}") {
              checkoutScmShallow()

              unstash 'xk_316_mc_bin'

              dir("tests") {
                createVenv(reqFile: "requirements.txt")
                dir("tools") {
                  copyArtifacts filter: 'Win/x64/xmos_mixer.exe', fingerprintArtifacts: true, projectName: 'XMOS/lib_xua/develop', flatten: true, selector: lastSuccessful()
                }

                withTools(params.TOOLS_VERSION) {
                  withVenv() {
                    dir("${env.VIRTUAL_ENV}/src/hardware-test-tools") {
                      withVS() {
                        sh "cmake -B build -G Ninja"
                        sh "ninja -C build"
                      }

                      dir("xsig") {
                        copyArtifacts filter: 'bin-windows-x86/xsig.exe', fingerprintArtifacts: true, projectName: 'xmos-int/xsig/master', flatten: true, selector: lastSuccessful()
                      }
                    } // dir("${env.VIRTUAL_ENV}/src/hardware-test-tools")
                    withXTAG(["usb_audio_mc_xcai_dut", "usb_audio_mc_xcai_harness"]) { xtagIds ->
                      sh "pytest -v --level ${params.TEST_LEVEL} --junitxml=pytest_result_windows10.xml \
                          -o xk_316_mc_dut=${xtagIds[0]} -o xk_316_mc_harness=${xtagIds[1]} "
                    }
                    archiveArtifacts artifacts: "${env.VIRTUAL_ENV}/src/hardware-test-tools/xsig/glitch.*.csv", fingerprint: true, allowEmptyArchive: true
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
        }  // Windows 10

        stage('Windows 11') {
          agent {
            label 'usb_audio && windows11 && xcore.ai-mcab'
          }
          steps {
            println "Stage running on ${env.NODE_NAME}"

            dir("sw_audio_analyzer") {
              copyArtifacts filter: '**/*.xe', fingerprintArtifacts: true, projectName: 'xmos-int/sw_audio_analyzer/master', selector: lastSuccessful()
              copyArtifacts filter: 'host_xscope_controller/bin_windows/xscope_controller.exe', fingerprintArtifacts: true, projectName: 'xmos-int/sw_audio_analyzer/master', selector: lastSuccessful()
            }

            dir("${REPO}") {
              checkoutScmShallow()

              unstash 'xk_316_mc_bin'

              dir("tests") {
                createVenv(reqFile: "requirements.txt")
                dir("tools") {
                  copyArtifacts filter: 'Win/x64/xmos_mixer.exe', fingerprintArtifacts: true, projectName: 'XMOS/lib_xua/develop', flatten: true, selector: lastSuccessful()
                }

                withTools(params.TOOLS_VERSION) {
                  withVenv() {
                    dir("${env.VIRTUAL_ENV}/src/hardware-test-tools") {
                      withVS() {
                        sh "cmake -B build -G Ninja"
                        sh "ninja -C build"
                      }

                      dir("xsig") {
                        copyArtifacts filter: 'bin-windows-x86/xsig.exe', fingerprintArtifacts: true, projectName: 'xmos-int/xsig/master', flatten: true, selector: lastSuccessful()
                      }
                    } // dir("${env.VIRTUAL_ENV}/src/hardware-test-tools")

                    withXTAG(["usb_audio_mc_xcai_dut", "usb_audio_mc_xcai_harness"]) { xtagIds ->
                      sh "pytest -v --level ${params.TEST_LEVEL} --junitxml=pytest_result_windows11.xml \
                          -o xk_316_mc_dut=${xtagIds[0]} -o xk_316_mc_harness=${xtagIds[1]} "
                    }
                    archiveArtifacts artifacts: "${REPO}/tests/pytest_result_windows11.xml", fingerprint: true, allowEmptyArchive: true
                  }
                }
              }
            }
          }
          post {
            always {
              archiveArtifacts artifacts: "${env.VIRTUAL_ENV}/src/hardware-test-tools/xsig/glitch.*.csv", fingerprint: true, allowEmptyArchive: true
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
