# Third-party software and models

The MIT license in this repository applies only to original LAI code and documentation contributed under that license. It does not change the terms of external software, services, models, weights, datasets, or templates.

| Component | Included here | Notes |
| --- | --- | --- |
| Visual Studio Code and its API | No | The Code - OSS source is MIT; Microsoft's Visual Studio Code distribution has separate product terms. Obtain the runtime from Microsoft and follow the applicable terms: https://github.com/microsoft/vscode |
| llama.cpp / llama-server | No | The upstream source currently uses MIT. Obtain it separately and review the selected version and bundled components: https://github.com/ggml-org/llama.cpp |
| Ministral 3 8B Instruct 2512 GGUF | No | The official model card currently identifies Apache-2.0 and includes a third-party-rights condition. The name is a tested default, not redistributed weights: https://huggingface.co/mistralai/Ministral-3-8B-Instruct-2512-GGUF |
| GGUF model files | No | Users supply their own compatible model. |
| Model chat templates | No | No extracted third-party template is redistributed. Use a template supplied or permitted by the chosen model/provider. |
| ripgrep, Git, Python, Node.js | No | Runtime/development tools are installed separately under their own terms. |
| `@vscode/vsce` 3.9.2 packaging tool | No | MIT-identified development tool fetched separately from npm; its dependencies are not bundled in the VSIX and require review if build tooling is redistributed: https://www.npmjs.com/package/@vscode/vsce |

Before redistributing a build or example containing third-party material, verify its exact origin, version, notices, and redistribution conditions. A reference in documentation is not a grant of rights or an endorsement.
