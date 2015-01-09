# About PyFlex

PyFlex is a tool for deploying and otherwise configuring a Flexpod. 

PyFlex operates on the DRY principle, and used a single, nonredundant source of data to deploy configuration artifacts throughout the various components in a Flexpod. The goal is to define your data in one place (a YAML configuration file), and PyFlex will automatically derive things from it.

Please consider this project an unstable alpha until otherwise notified here. This is currently under active development, and I am trying to get to a point where the UCS portion works. After I can make a first release with that functionality, I will perform all additional functionality in a dev branch.

# Dependencies

- Python (>=2.7)
- [Cisco UCS Python SDK 0.8.2](https://communities.cisco.com/docs/DOC-37174)
- Other dependencies listed in requirements.txt

# Installation

Simply run

````python setup.py install````

to build the library and automatically install dependencies.

# Benefits
- (roadmap) Built to be idempotent - run once, multiple times, whatever. Your config will be made true.
- Engineers don't need to worry about all the nerd knobs. Best practices are implemented in code. Wherever possible, configuration data is pulled from existing infrastructure, rather than a human being.
- Documentation is simplified. We can create templates, and just insert values. No snowflakes.
- (roadmap) Centralized administration of multiple domains without a bloated, stateful application like UCS Central. Why create an unnecessary, always-on point of management you don't need?

# Notes for Running on Windows

If you have issues with pycrypto on Windows while building this library, just download the pre-built binaries here:
http://www.voidspace.org.uk/python/modules.shtml#pycrypto

# References

This is a list of vendor-supplied documentation used as references in building PyFlex.

- [Flexpod Design Guide - ESXi 5.5](http://www.cisco.com/c/dam/en/us/td/docs/unified_computing/ucs/UCS_CVDs/flexpod_esxi55u1_design.pdf)
- [Flexpod Deployment Guide - ESXi 5.5](http://www.cisco.com/c/dam/en/us/td/docs/unified_computing/ucs/UCS_CVDs/flexpod_esxi55u1.pdf)

<!-- NOT USED YET - here for future reference - http://www.cisco.com/c/dam/en/us/td/docs/unified_computing/ucs/UCS_CVDs/flexpod_esxi55u1_n9k.pdf -->
