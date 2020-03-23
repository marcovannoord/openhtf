# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6]

### Added
- Add basic plugs types: Comport, SSH, VISA. The dependencies associated with each plug is installed using an extra named `plugs.comport`, `plugs.ssh`, etc. 
- SSH Plug `execute_command` now accepts a `return_resp_obj` parameter that can be set to True to receive an object that contains the following attributes: `exit_code`, `std_output`, `err_output`, `output` (err + std output)

### Deprecated