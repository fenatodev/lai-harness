import json
from pathlib import Path
import subprocess
import unittest


REPO = Path(__file__).parents[1]
EXTENSION = REPO / "vscode-extension"


class ExtensionTest(unittest.TestCase):
    def test_agent_path_configuration_is_declared(self):
        package = json.loads((EXTENSION / "package.json").read_text())
        setting = package["contributes"]["configuration"]["properties"]["lai.agentPath"]
        self.assertEqual(setting["type"], "string")
        self.assertEqual(setting["default"], "")

    def test_configured_agent_path_overrides_default(self):
        script = r"""
const Module = require('module');
const originalLoad = Module._load;
Module._load = function(request, parent, isMain) {
  if (request === 'vscode') {
    return {workspace: {getConfiguration: () => ({get: () => '/tmp/synthetic-agent'})}};
  }
  return originalLoad(request, parent, isMain);
};
const extension = require(process.argv[1]);
if (extension.resolveAgentPath() !== '/tmp/synthetic-agent') process.exit(1);
"""
        subprocess.run(
            ["node", "-e", script, str(EXTENSION / "extension.js")],
            check=True,
            text=True,
            capture_output=True,
        )


    def test_stderr_helpers_preserve_errors_and_filter_progress(self):
        script = r"""
const Module = require('module');
const originalLoad = Module._load;

Module._load = function(request, parent, isMain) {
  if (request === 'vscode') {
    return {
      workspace: {
        getConfiguration: () => ({get: () => ''})
      }
    };
  }
  return originalLoad(request, parent, isMain);
};

const extension = require(process.argv[1]);

if (!extension.isProgressStderrLine('[bash] {"command":"test"}')) process.exit(1);
if (extension.isProgressStderrLine('Agent stopped: overall round limit reached.')) process.exit(2);

let diagnostic = '';

diagnostic = extension.appendStderrDiagnostic(
  diagnostic,
  '[bash] {"command":"python3 -m unittest"}'
);

diagnostic = extension.appendStderrDiagnostic(
  diagnostic,
  'Agent stopped: overall round limit reached (14 rounds).'
);

if (
  diagnostic !==
  'Agent stopped: overall round limit reached (14 rounds).'
) process.exit(3);

if (
  extension.appendStderrDiagnostic('', '1234567890', 6) !== '567890'
) process.exit(4);
"""

        subprocess.run(
            ["node", "-e", script, str(EXTENSION / "extension.js")],
            check=True,
            text=True,
            capture_output=True,
        )


if __name__ == "__main__":
    unittest.main()
