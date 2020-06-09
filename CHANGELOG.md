# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.2]

### Added
- Gitlab CI configuration.

## [0.6.1]

### Fixed
- ComportInterface timeout would always at least be 10 seconds because of the underlying call to next_line without a timeout argument.
- TestPlan now accepts a store_location argument to overwrite default site data dir location.

## [0.6]

### Added
- Add basic plugs types: Comport, SSH, VISA. The dependencies associated with each plug is installed using an extra named `plugs.comport`, `plugs.ssh`, etc. 
- SSH Plug `execute_command` returns an object that contains the following attributes: `exit_code`, `std_output`, `err_output`, `output` (err + std output)
- SSH Plug raises a timeout exception (SSHTimeoutError) when the client timeout is reached.
- Adds Sphinx-based documentation of the following modules:
  - TestPlan
  - OpenHTF Configuration & default values
  - Plugs: Comport, SSH and VISA.
- Added the spintop-openhtf examples in source at `spintop_openhtf.examples`

### Changed
- Spintop-OpenHTF with the GUI now needs to be installed with the [server] extra (pip install spintop-openhtf[server]==0.6.0). This is to avoid conflicts with the old version of tornado (4.0) that openhtf uses.
- Changed imports of ABCs from `collections` to `collections.abc` to comply with Python 3.8 deprecation.
- The examples of openhtf are now in the package `openhtf.examples` instead of the top-level package `examples`

### Fixed
- Issue #13. An object reference bug sometimes caused the frontend to not be notified when a new test started.