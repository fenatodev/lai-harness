import json
from pathlib import Path
import subprocess
import unittest


REPO = Path(__file__).parents[1]
EXTENSION = REPO / "vscode-extension"


class ExtensionTest(unittest.TestCase):
    def test_package_branding_preserves_compatibility_ids(self):
        package = json.loads((EXTENSION / "package.json").read_text())
        self.assertEqual(package["displayName"], "lai harness")
        self.assertIn("lai harness", package["description"])
        self.assertEqual(package["name"], "lai-chat")
        self.assertEqual(package["publisher"], "lai-local-agent")
        participant = package["contributes"]["chatParticipants"][0]
        self.assertEqual(participant["name"], "lai")
        self.assertEqual(participant["fullName"], "lai harness")
        self.assertEqual(participant["id"], "lai-local-agent.lai")
        self.assertEqual(package["contributes"]["configuration"]["title"], "lai harness")
        command_names = {cmd["name"] for cmd in participant["commands"]}
        self.assertTrue({"diagnose", "ci-fix", "release", "readiness"}.issubset(command_names))
        self.assertEqual(
            package["repository"]["url"],
            "https://github.com/fenatodev/lai-harness.git",
        )

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


    def test_workspace_selection_and_write_safety(self):
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

let target = extension.selectExecutionCwd({
  workspacePaths: ['/repo/content-pipeline'],
  activeFilePath: '/tmp/outside.py',
  homeDir: '/home/test'
});

if (target.cwd !== '/repo/content-pipeline') process.exit(1);
if (!target.hasWorkspace) process.exit(2);
if (target.ambiguous) process.exit(3);

target = extension.selectExecutionCwd({
  workspacePaths: ['/repo/one', '/repo/two'],
  activeFileWorkspacePath: '/repo/two',
  activeFilePath: '/repo/two/app.py',
  homeDir: '/home/test'
});

if (target.cwd !== '/repo/two') process.exit(4);
if (target.ambiguous) process.exit(5);

target = extension.selectExecutionCwd({
  workspacePaths: ['/repo/one', '/repo/two'],
  homeDir: '/home/test'
});

if (!target.ambiguous) process.exit(6);

if (
  !extension.workspaceSafetyError('implement', target)
) process.exit(7);

target = extension.selectExecutionCwd({
  workspacePaths: [],
  activeFilePath: '/tmp/file.py',
  homeDir: '/home/test'
});

if (target.cwd !== '/tmp') process.exit(8);

if (
  !extension.workspaceSafetyError('fix', target)
) process.exit(9);

if (
  extension.workspaceSafetyError('plan', target) !== ''
) process.exit(10);

if (
  extension.workspaceSafetyError('diagnose', target) !== ''
) process.exit(15);

if (
  !extension.workspaceSafetyError('ci-fix', target)
) process.exit(16);

target = extension.selectExecutionCwd({
  workspacePaths: ['/repo/safe'],
  homeDir: '/home/test'
});

if (
  extension.workspaceSafetyError('implement', target) !== ''
) process.exit(11);

if (
  extension.shouldIncludeActiveFileContext('implement', false)
) process.exit(12);

if (
  !extension.shouldIncludeActiveFileContext('implement', true)
) process.exit(13);

if (
  !extension.shouldIncludeActiveFileContext('plan', false)
) process.exit(14);
"""

        subprocess.run(
            ["node", "-e", script, str(EXTENSION / "extension.js")],
            check=True,
            text=True,
            capture_output=True,
        )


if __name__ == "__main__":
    unittest.main()
