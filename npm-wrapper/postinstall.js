#!/usr/bin/env node
/**
 * Post-install script for ipcom-marketing-ai
 * Automatically configures MCP for Claude Code if available
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

console.log('\n🚀 OSP Marketing Tools - Post-install Setup');
console.log('='.repeat(50));

// Check if running in CI or non-interactive environment
if (process.env.CI || process.env.NO_INTERACTIVE || !process.stdout.isTTY) {
    console.log('⚠️  Non-interactive environment detected. Skipping auto-setup.');
    console.log('📝 To configure manually, run: ipcom-marketing-ai configure');
    process.exit(0);
}

// Find Python
function findPython() {
    const pythonCommands = ['python3', 'python', 'py'];

    for (const cmd of pythonCommands) {
        try {
            const result = require('child_process').execSync(`${cmd} --version`, {
                encoding: 'utf8',
                stdio: 'pipe'
            });
            if (result.includes('Python')) {
                return cmd;
            }
        } catch (e) {
            // Continue trying
        }
    }
    return null;
}

// Check if Claude Code might be installed
function isClaudeCodeLikely() {
    const home = os.homedir();
    const possiblePaths = [
        path.join(home, 'Library', 'Application Support', 'Claude'),
        path.join(home, '.claude'),
        path.join(home, '.config', 'claude'),
        path.join(process.env.APPDATA || '', 'Claude'),
    ];

    for (const p of possiblePaths) {
        if (fs.existsSync(p)) {
            return true;
        }
    }
    return false;
}

// Main setup
async function setup() {
    console.log('\n📋 Checking environment...');

    // Find Python
    const pythonCmd = findPython();
    if (!pythonCmd) {
        console.log('⚠️  Python not found. MCP configuration requires Python.');
        console.log('📝 Install Python from: https://www.python.org/downloads/');
        console.log('\n✅ You can still use standalone mode:');
        console.log('   npx ipcom-marketing-ai demo');
        return;
    }
    console.log(`✓ Python found: ${pythonCmd}`);

    // Check for Claude Code
    if (!isClaudeCodeLikely()) {
        console.log('ℹ️  Claude Code not detected.');
        console.log('\n✅ Available modes:');
        console.log('   • Standalone: npx ipcom-marketing-ai demo');
        console.log('   • Configure later: npx ipcom-marketing-ai configure');
        return;
    }

    console.log('✓ Claude Code installation detected');
    console.log('\n🔧 Attempting automatic MCP configuration...');

    // Path to setup script
    const setupScript = path.join(__dirname, '..', 'setup-mcp.py');

    if (!fs.existsSync(setupScript)) {
        console.log('⚠️  Setup script not found. Please run manually:');
        console.log('   npx ipcom-marketing-ai configure');
        return;
    }

    // Run setup script silently
    const setup = spawn(pythonCmd, [setupScript, '--silent'], {
        stdio: 'inherit'
    });

    setup.on('close', (code) => {
        if (code === 0) {
            console.log('\n✅ MCP configuration successful!');
            console.log('\n📝 Next steps:');
            console.log('   1. Restart Claude Code');
            console.log('   2. Tools will be available automatically');
            console.log('\n💡 Alternative modes:');
            console.log('   • Standalone demo: npx ipcom-marketing-ai demo');
            console.log('   • Reconfigure: npx ipcom-marketing-ai configure');
        } else {
            console.log('\n⚠️  Automatic configuration failed.');
            console.log('\n📝 Manual options:');
            console.log('   • Configure manually: npx ipcom-marketing-ai configure');
            console.log('   • Use standalone mode: npx ipcom-marketing-ai demo');
        }

        console.log('\n🙏 Thank you for installing OSP Marketing Tools!');
        console.log('📧 Support: contato@openpartners.com.br');
        console.log('='.repeat(50));
    });

    setup.on('error', (err) => {
        console.error('❌ Error running setup:', err.message);
        console.log('\n📝 Please configure manually:');
        console.log('   npx ipcom-marketing-ai configure');
    });
}

// Run setup
setup().catch(err => {
    console.error('❌ Setup error:', err);
    process.exit(1);
});
