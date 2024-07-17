# TofuPilot Python client

[![PyPI version](https://badge.fury.io/py/tofupilot.svg)](https://badge.fury.io/py/tofupilot)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The official open-source Python client for [TofuPilot](https://tofupilot.com). Quickly and seamlessly integrate all your hardware test runs into one app with just a few lines of Python.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Installation

Package can be installed via pip

```bash
pip install tofupilot
```

## Usage

### API Key Setup

Running the examples requires a TofuPilot AI API key.
You can find examples in the examples/ directory.

1. Get your own TofuPilot API Key: https://docs.tofupilot.com/api-key
2. Set your TofuPilot API Key as an environment variable. You only need to do this once.

```bash
# set TofuPilot API Key (using zsh for example)

$ echo 'export TOFUPILOT_API_KEY=[your_key_here]' >> ~/.zshenv

# reload the environment (or just quit and open a new terminal)

$ source ~/.zshenv
```

## Contributing

Please read [CONTRIBUTING](./CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) for details.

## Contact

If you have any questions or feedback, feel free to open an issue or contact us at support@tofupilot.com.
