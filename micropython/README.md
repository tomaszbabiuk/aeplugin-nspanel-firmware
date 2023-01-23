Required VSCode extensions:
* https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance
* https://marketplace.visualstudio.com/items?itemName=ms-python.python
* https://marketplace.visualstudio.com/items?itemName=jkearins.action-buttons-ext
* https://marketplace.visualstudio.com/items?itemName=oderwat.indent-rainbow
* Disable or uninstall the PyLint extension (it collides with Pylance)

Required python packages
* pip install -U micropython-esp32-stubs
* pip install -U adafruit-ampy

Use with venv: https://micropython-stubs.readthedocs.io/en/doc_update/22_vscode.html#configure-vscode-pylance

Final VS Code configuration (settings.json):
```bash
{
    "python.languageServer": "Pylance",
    "python.analysis.typeCheckingMode": "basic",
    "python.analysis.diagnosticSeverityOverrides": {
        "reportMissingModuleSource": "none"
    },
    "python.analysis.typeshedPaths": [
        ".venv/Lib/python3.10/site-packages"
    ],
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "actionButtons": {
        "loadNpmCommands":false, // Disables automatic generation of actions for npm commands.
        "commands": [
            {
                "cwd": "${workspaceFolder}",
                "name": "Upload main.py",
                "singleInstance": true,
                "command": "ampy --port /dev/tty.usbserial-210 put src/main.py",
            },
            {
                "cwd": "${workspaceFolder}",
                "name": "Upload boot.py",
                "singleInstance": true,
                "command": "ampy --port /dev/tty.usbserial-210 put src/boot.py",
            },
            {
                "cwd": "${workspaceFolder}",
                "name": "REPL",
                "singleInstance": true,
                "command": "screen /dev/tty.usbserial-210 115200",
            }
        ]
    }
}
```
