tap 'homebrew/core'
tap 'xmos/tools', 'git@github.com:xmos/homebrew-tools.git'

brew 'ruby'
brew 'perl'
brew 'cpanm'

brew 'python'
# Build dependencies for Python (when compiled with pyenv)
brew 'openssl'
brew 'readline'
brew 'sqlite3'
brew 'xz'
brew 'zlib'
brew 'cmake'

# Dependencies for xtag reset functionality
brew 'libusb'

if OS.linux?
    brew 'readline'
    brew 'gcc'
end
