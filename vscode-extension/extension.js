const vscode = require('vscode');
const cp = require('child_process');
const path = require('path');
const os = require('os');

const STDERR_PROGRESS_PREFIXES = [
    '[read]',
    '[search]',
    '[list]',
    '[git]',
    '[inspect]',
    '[patch]',
    '[project]',
    '[edit]',
    '[create]',
    '[bash]'
];

const MAX_STDERR_DIAGNOSTIC_CHARS = 4000;

function isProgressStderrLine(line) {
    const trimmed = String(line || '').trim();
    return STDERR_PROGRESS_PREFIXES.some(prefix =>
        trimmed.startsWith(prefix)
    );
}

function appendStderrDiagnostic(current, line, maxChars = MAX_STDERR_DIAGNOSTIC_CHARS) {
    const trimmed = String(line || '').trim();

    if (!trimmed || isProgressStderrLine(trimmed)) {
        return current;
    }

    const combined = current
        ? `${current}\n${trimmed}`
        : trimmed;

    return combined.length <= maxChars
        ? combined
        : combined.slice(-maxChars);
}

const WRITE_COMMANDS = new Set([
    'fix',
    'refactor',
    'implement'
]);

function selectExecutionCwd({
    workspacePaths = [],
    activeFileWorkspacePath = '',
    activeFilePath = '',
    homeDir = os.homedir()
}) {
    const paths = Array.isArray(workspacePaths)
        ? workspacePaths.filter(Boolean)
        : [];

    if (activeFileWorkspacePath) {
        return {
            cwd: activeFileWorkspacePath,
            hasWorkspace: true,
            ambiguous: false
        };
    }

    if (paths.length === 1) {
        return {
            cwd: paths[0],
            hasWorkspace: true,
            ambiguous: false
        };
    }

    if (paths.length > 1) {
        return {
            cwd: paths[0],
            hasWorkspace: true,
            ambiguous: true
        };
    }

    if (activeFilePath) {
        return {
            cwd: path.dirname(activeFilePath),
            hasWorkspace: false,
            ambiguous: false
        };
    }

    return {
        cwd: homeDir,
        hasWorkspace: false,
        ambiguous: false
    };
}

function shouldIncludeActiveFileContext(command, hasFileWorkspace) {
    return (
        !WRITE_COMMANDS.has(command)
        || Boolean(hasFileWorkspace)
    );
}

function workspaceSafetyError(command, target) {
    if (!WRITE_COMMANDS.has(command)) {
        return '';
    }

    if (!target.hasWorkspace) {
        return (
            'Abra uma pasta/repositório no VS Code antes de usar ' +
            `/${command}.`
        );
    }

    if (target.ambiguous) {
        return (
            'Há vários workspaces abertos. Abra um arquivo do ' +
            `repositório alvo antes de usar /${command}.`
        );
    }

    return '';
}

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
            stream.markdown('Digite uma tarefa para o lai harness.');
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
        const workspaceFolders =
            vscode.workspace.workspaceFolders || [];

        let fileWorkspace = null;
        let activeFilePath = '';

        if (editor && editor.document.uri.scheme === 'file') {
            activeFilePath = editor.document.uri.fsPath;
            fileWorkspace = vscode.workspace.getWorkspaceFolder(
                editor.document.uri
            );
        }

        const executionTarget = selectExecutionCwd({
            workspacePaths: workspaceFolders.map(
                folder => folder.uri.fsPath
            ),
            activeFileWorkspacePath:
                fileWorkspace?.uri.fsPath || '',
            activeFilePath,
            homeDir: os.homedir()
        });

        const cwd = executionTarget.cwd;
        const extraContext = [];

        const workspaceError = workspaceSafetyError(
            request.command,
            executionTarget
        );

        if (workspaceError) {
            stream.markdown(workspaceError);
            return;
        }

        if (WRITE_COMMANDS.has(request.command)) {
            stream.progress(`Workspace: ${cwd}`);
        }

        const includeActiveFileContext =
            shouldIncludeActiveFileContext(
                request.command,
                fileWorkspace
            );

        if (
            editor
            && editor.document.uri.scheme === 'file'
            && includeActiveFileContext
        ) {
            const document = editor.document;

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
            explain: 'lai harness explicando seleção...',
            fix: 'lai harness investigando e corrigindo...',
            test: 'lai harness executando testes...',
            review: 'lai harness revisando código...',
            debug: 'lai harness investigando a causa...',
            refactor: 'lai harness refatorando e validando...',
            security: 'lai harness revisando segurança...',
            plan: 'lai harness planejando implementação...',
            implement: 'lai harness implementando e validando...',
            handoff: 'lai harness preparando handoff...',
            clearcontext: 'lai harness limpando contexto local...',
            status: 'lai harness lendo status do workspace...',
            metrics: 'lai harness lendo métricas locais...',
            audit: 'lai harness lendo trilha de auditoria...'
        };

        stream.progress(
            progressLabels[request.command] || 'lai harness executando...'
        );

        await new Promise((resolve, reject) => {
            const child = cp.spawn(agentPath, agentArgs, {
                cwd,
                env: process.env,
                stdio: ['ignore', 'pipe', 'pipe']
            });

            let stderrBuffer = '';
            let stderrDiagnostics = '';
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

                    if (isProgressStderrLine(trimmed)) {
                        stream.progress(trimmed);
                    } else {
                        stderrDiagnostics = appendStderrDiagnostic(
                            stderrDiagnostics,
                            trimmed
                        );
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

                const trailingStderr = stderrBuffer.trim();

                if (trailingStderr) {
                    if (isProgressStderrLine(trailingStderr)) {
                        stream.progress(trailingStderr);
                    } else {
                        stderrDiagnostics = appendStderrDiagnostic(
                            stderrDiagnostics,
                            trailingStderr
                        );
                    }
                }

                if (code !== 0) {
                    reject(
                        new Error(
                            `local-agent terminou com código ${code}` +
                            (stderrDiagnostics
                                ? `: ${stderrDiagnostics}`
                                : '')
                        )
                    );
                    return;
                }

                if (!producedOutput) {
                    stream.markdown(
                        '_lai harness terminou sem produzir resposta._'
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
    resolveAgentPath,
    isProgressStderrLine,
    appendStderrDiagnostic,
    selectExecutionCwd,
    workspaceSafetyError,
    shouldIncludeActiveFileContext
};
