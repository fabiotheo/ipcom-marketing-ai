#!/usr/bin/env node

/**
 * NPM Wrapper for IPCOM Marketing AI MCP Server
 * Enhanced with multiple modes: configure, demo, and MCP server
 */

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { existsSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Parse command line arguments
const args = process.argv.slice(2);
const command = args[0];

/**
 * Show help message
 */
function showHelp() {
    console.log(`
🎯 IPCOM Marketing AI - Zero-Config Marketing Tools
===================================================

Usage: ipcom-marketing-ai [command] [options]

Commands:
  (default)     Start MCP server for Claude Code
  configure     Configure MCP for Claude Code
  demo          Run standalone demo (no setup required)
  status        Check current configuration
  help          Show this help message

Examples:
  ipcom-marketing-ai              # Start MCP server
  ipcom-marketing-ai configure    # Setup Claude Code integration
  ipcom-marketing-ai demo         # Run interactive demo

Learn more: https://github.com/fabiotheo/ipcom-marketing-ai
`);
    process.exit(0);
}

/**
 * Check if uvx is available
 */
function checkUvx() {
    return new Promise((resolve) => {
        const uvxCheck = spawn('uvx', ['--version'], { stdio: 'ignore' });
        uvxCheck.on('close', (code) => {
            resolve(code === 0);
        });
        uvxCheck.on('error', () => {
            resolve(false);
        });
    });
}

/**
 * Check if Python is available
 */
function checkPython() {
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

/**
 * Install uv if uvx is not available
 */
function installUv() {
    return new Promise((resolve, reject) => {
        console.log('📦 Installing uv...');
        const pip = spawn('pip', ['install', 'uv'], {
            stdio: ['inherit', 'inherit', 'inherit']
        });

        pip.on('close', (code) => {
            if (code === 0) {
                console.log('✅ uv installed successfully');
                resolve();
            } else {
                reject(new Error('Failed to install uv'));
            }
        });
    });
}

/**
 * Run configuration setup
 */
async function runConfigure() {
    console.log('🔧 Configuring MCP for Claude Code...\n');

    const pythonCmd = checkPython();
    if (!pythonCmd) {
        console.error('❌ Python not found. Please install Python 3.8+');
        console.error('📝 Download from: https://www.python.org/downloads/');
        process.exit(1);
    }

    // Path to setup script
    const setupScript = join(__dirname, '..', 'setup-mcp.py');

    if (!existsSync(setupScript)) {
        console.error('❌ Setup script not found');
        console.error('📝 Please reinstall: npm install -g ipcom-marketing-ai');
        process.exit(1);
    }

    const setup = spawn(pythonCmd, [setupScript], {
        stdio: 'inherit'
    });

    setup.on('close', (code) => {
        process.exit(code);
    });

    setup.on('error', (err) => {
        console.error('❌ Error running setup:', err.message);
        process.exit(1);
    });
}

/**
 * Run standalone demo
 */
async function runDemo() {
    console.log('🎭 Starting Interactive Buyer Persona Generator (Standalone Mode)...\n');

    const pythonCmd = checkPython();
    if (!pythonCmd) {
        console.error('❌ Python not found. Please install Python 3.8+');
        console.error('📝 Download from: https://www.python.org/downloads/');
        process.exit(1);
    }

    // Path to demo script
    const demoScript = join(__dirname, '..', 'demo_standalone.py');

    if (!existsSync(demoScript)) {
        console.error('❌ Demo script not found');
        console.error('📝 Please reinstall: npm install -g ipcom-marketing-ai');
        process.exit(1);
    }

    const demo = spawn(pythonCmd, [demoScript], {
        stdio: 'inherit'
    });

    demo.on('close', (code) => {
        process.exit(code);
    });

    demo.on('error', (err) => {
        console.error('❌ Error running demo:', err.message);
        process.exit(1);
    });
}

/**
 * Check configuration status
 */
async function checkStatus() {
    console.log('📊 Checking OSP Marketing Tools Status...\n');

    const pythonCmd = checkPython();
    console.log(`✓ Python: ${pythonCmd || 'Not found'}`);

    const hasUvx = await checkUvx();
    console.log(`✓ uvx: ${hasUvx ? 'Installed' : 'Not installed'}`);

    // Check for Claude Code config
    const os = require('os');
    const path = require('path');
    const fs = require('fs');
    const home = os.homedir();

    const configPaths = [
        path.join(home, 'Library', 'Application Support', 'Claude', 'claude_desktop_config.json'),
        path.join(home, '.claude', 'claude_desktop_config.json'),
        path.join(home, '.config', 'claude', 'claude_desktop_config.json'),
    ];

    let mcpConfigured = false;
    for (const configPath of configPaths) {
        if (fs.existsSync(configPath)) {
            try {
                const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
                if (config.mcpServers && config.mcpServers['osp-marketing-tools']) {
                    mcpConfigured = true;
                    break;
                }
            } catch (e) {
                // Continue checking
            }
        }
    }

    console.log(`✓ MCP Configured: ${mcpConfigured ? 'Yes' : 'No'}`);

    console.log('\n📝 Available commands:');
    if (!mcpConfigured) {
        console.log('   • Configure MCP: ipcom-marketing-ai configure');
    }
    console.log('   • Run demo: ipcom-marketing-ai demo');
    console.log('   • Start server: ipcom-marketing-ai');

    process.exit(0);
}

/**
 * Start the OSP Marketing Tools MCP Server
 */
async function startServer() {
    try {
        console.log('🚀 Starting IPCOM Marketing AI MCP Server...');
        console.log('📝 For standalone demo, use: ipcom-marketing-ai demo\n');

        // Check if uvx is available
        const hasUvx = await checkUvx();

        if (!hasUvx) {
            await installUv();
        }

        // Start the MCP server using uvx
        const server = spawn('uvx', [
            '--from',
            'git+https://github.com/fabiotheo/ipcom-marketing-ai@main',
            'osp_marketing_tools'
        ], {
            stdio: ['inherit', 'inherit', 'inherit']
        });

        // Handle server lifecycle
        server.on('close', (code) => {
            if (code !== 0) {
                console.error(`\n❌ Server exited with code ${code}`);
                console.error('\n💡 Troubleshooting:');
                console.error('   • Configure: ipcom-marketing-ai configure');
                console.error('   • Standalone: ipcom-marketing-ai demo');
                console.error('   • Check status: ipcom-marketing-ai status');
                process.exit(code);
            }
        });

        server.on('error', (error) => {
            console.error('❌ Failed to start server:', error.message);
            console.error('\n💡 Try standalone mode: ipcom-marketing-ai demo');
            process.exit(1);
        });

        // Handle graceful shutdown
        process.on('SIGINT', () => {
            console.log('\n🛑 Shutting down server...');
            server.kill('SIGINT');
        });

        process.on('SIGTERM', () => {
            console.log('\n🛑 Shutting down server...');
            server.kill('SIGTERM');
        });

    } catch (error) {
        console.error('❌ Error starting server:', error.message);
        console.error('\n💡 Try standalone mode: ipcom-marketing-ai demo');
        process.exit(1);
    }
}

// Main command router
async function main() {
    switch(command) {
        case 'configure':
        case 'config':
        case 'setup':
            await runConfigure();
            break;

        case 'demo':
        case 'standalone':
        case 'test':
            await runDemo();
            break;

        case 'status':
        case 'check':
            await checkStatus();
            break;

        case 'help':
        case '--help':
        case '-h':
            showHelp();
            break;

        case undefined:
        case 'start':
        case 'server':
            // Default action - start MCP server
            await startServer();
            break;

        default:
            console.error(`❌ Unknown command: ${command}`);
            console.error('📝 Use "ipcom-marketing-ai help" for available commands');
            process.exit(1);
    }
}

// Run main function
main().catch(err => {
    console.error('❌ Fatal error:', err);
    process.exit(1);
});
