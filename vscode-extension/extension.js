const vscode = require('vscode');
const cp = require('child_process');
const path = require('path');
const os = require('os');

function resolveAgentPath() {
    const configuredAgentPath = vscode.workspace
        .getConfiguration('lai')
        .get('agentPath', '');
    return configuredAgentPath || path.join(
        os.homedir(), '.local', 'bin', 'local-agent'
    );
}

function activate(context) {
    const handler = async (request, chatContext, stream, token) => {
        const isExplain = request.command === 'explain';
        const isContextCommand =
            request.command === 'handoff' ||
            request.command === 'clearcontext' ||
            request.command === 'status' ||
            request.command === 'metrics' ||
            request.command === 'audit';

        const typedPrompt = request.prompt.trim();

        const promptOptional =
            isExplain ||
            isContextCommand;

        if (!typedPrompt && !promptOptional) {
            stream.markdown('Digite uma tarefa para o Local AI.');
            return;
        }

        const defaultPrompts = {
            explain: 'Explique apenas o que faz a seleção atual.',
            handoff: '',
            clearcontext: '',
            status: '',
            metrics: '',
            audit: ''
        };

        const userPrompt =
            typedPrompt ||
            defaultPrompts[request.command] ||
            '';

        const editor = vscode.window.activeTextEditor;
        const workspace = vscode.workspace.workspaceFolders?.[0];

        let cwd = workspace?.uri.fsPath || os.homedir();
        const extraContext = [];

        if (editor && editor.document.uri.scheme === 'file') {
            const document = editor.document;
            const fileWorkspace = vscode.workspace.getWorkspaceFolder(document.uri);

            if (fileWorkspace) {
                cwd = fileWorkspace.uri.fsPath;
            } else {
                cwd = path.dirname(document.uri.fsPath);
            }

            const filename = fileWorkspace
                ? path.relative(fileWorkspace.uri.fsPath, document.uri.fsPath)
                : document.uri.fsPath;

            extraContext.push(`Arquivo ativo no VS Code: ${filename}`);

            if (
                request.command === 'fix' ||
                request.command === 'debug' ||
                request.command === 'implement'
            ) {
                const diagnostics = vscode.languages
                    .getDiagnostics(document.uri)
                    .filter(d =>
                        d.severity === vscode.DiagnosticSeverity.Error ||
                        d.severity === vscode.DiagnosticSeverity.Warning
                    )
                    .slice(0, 8);

                if (diagnostics.length) {
                    const formattedDiagnostics = diagnostics
                        .map(d => {
                            const severity =
                                d.severity === vscode.DiagnosticSeverity.Error
                                    ? 'ERROR'
                                    : 'WARNING';

                            const line = d.range.start.line + 1;
                            const source = d.source
                                ? ` source=${d.source}`
                                : '';

                            let code = '';
                            if (d.code !== undefined && d.code !== null) {
                                const value =
                                    typeof d.code === 'object'
                                        ? d.code.value
                                        : d.code;
                                code = ` code=${String(value)}`;
                            }

                            const message = d.message
                                .replace(/\s+/g, ' ')
                                .slice(0, 300);

                            return (
                                `- ${severity} L${line}` +
                                `${source}${code}: ${message}`
                            );
                        })
                        .join('\n');

                    extraContext.push(
                        `Diagnósticos atuais do VS Code para ${filename}:\n` +
                        formattedDiagnostics
                    );
                }
            }

            if (!editor.selection.isEmpty) {
                let selected = document.getText(editor.selection);
                const MAX_SELECTION_CHARS = 800;

                if (selected.length > MAX_SELECTION_CHARS) {
                    selected =
                        selected.slice(0, MAX_SELECTION_CHARS) +
                        '\n[seleção truncada pelo VS Code para manter o agente rápido]';
                }

                const start = editor.selection.start.line + 1;
                const end = editor.selection.end.line + 1;

                extraContext.push(
                    `Seleção ativa, linhas ${start}-${end}:\n${selected}`
                );
            }
        }

        let prompt = userPrompt;

        if (
            extraContext.length &&
            !isContextCommand
        ) {
            prompt +=
                '\n\nContexto fornecido pelo VS Code:\n' +
                extraContext.join('\n\n');
        }

        const agentPath = resolveAgentPath();

        const commandModes = {
            explain: '--selection',
            fix: '--fix',
            test: '--test',
            review: '--review',
            debug: '--debug',
            refactor: '--refactor',
            security: '--security',
            plan: '--plan',
            implement: '--implement',
            handoff: '--handoff',
            clearcontext: '--clear-context',
            status: '--status',
            metrics: '--metrics',
            audit: '--audit'
        };

        const cliMode = commandModes[request.command];

        const agentArgs = cliMode
            ? [cliMode, prompt]
            : [prompt];

        const progressLabels = {
            explain: 'Local AI explicando seleção...',
            fix: 'Local AI investigando e corrigindo...',
            test: 'Local AI executando testes...',
            review: 'Local AI revisando código...',
            debug: 'Local AI investigando a causa...',
            refactor: 'Local AI refatorando e validando...',
            security: 'Local AI revisando segurança...',
            plan: 'Local AI planejando implementação...',
            implement: 'Local AI implementando e validando...',
            handoff: 'Local AI preparando handoff...',
            clearcontext: 'Local AI limpando contexto local...',
            status: 'Local AI lendo status do workspace...',
            metrics: 'Local AI lendo métricas locais...',
            audit: 'Local AI lendo trilha de auditoria...'
        };

        stream.progress(
            progressLabels[request.command] || 'Local AI executando...'
        );

        await new Promise((resolve, reject) => {
            const child = cp.spawn(agentPath, agentArgs, {
                cwd,
                env: process.env,
                stdio: ['ignore', 'pipe', 'pipe']
            });

            let stderrBuffer = '';
            let producedOutput = false;

            const cancellation = token.onCancellationRequested(() => {
                child.kill('SIGTERM');
            });

            child.stdout.setEncoding('utf8');
            child.stderr.setEncoding('utf8');

            child.stdout.on('data', chunk => {
                producedOutput = true;
                stream.markdown(chunk);
            });

            child.stderr.on('data', chunk => {
                stderrBuffer += chunk;

                const lines = stderrBuffer.split(/\r?\n/);
                stderrBuffer = lines.pop() || '';

                for (const line of lines) {
                    const trimmed = line.trim();

                    if (
                        trimmed.startsWith('[read]') ||
                        trimmed.startsWith('[search]') ||
                        trimmed.startsWith('[list]') ||
                        trimmed.startsWith('[git]') ||
                        trimmed.startsWith('[inspect]') ||
                        trimmed.startsWith('[patch]') ||
                        trimmed.startsWith('[project]') ||
                        trimmed.startsWith('[edit]') ||
                        trimmed.startsWith('[create]') ||
                        trimmed.startsWith('[bash]')
                    ) {
                        stream.progress(trimmed);
                    }
                }
            });

            child.on('error', error => {
                cancellation.dispose();
                reject(error);
            });

            child.on('close', code => {
                cancellation.dispose();

                if (token.isCancellationRequested) {
                    resolve();
                    return;
                }

                if (code !== 0) {
                    reject(
                        new Error(
                            `local-agent terminou com código ${code}` +
                            (stderrBuffer.trim()
                                ? `: ${stderrBuffer.trim()}`
                                : '')
                        )
                    );
                    return;
                }

                if (!producedOutput) {
                    stream.markdown(
                        '_Local AI terminou sem produzir resposta._'
                    );
                }

                resolve();
            });
        });
    };

    const participant = vscode.chat.createChatParticipant(
        'lai-local-agent.lai',
        handler
    );

    context.subscriptions.push(participant);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate,
    resolveAgentPath
};
