#!/usr/bin/env node

/**
 * NPM Wrapper for IPCOM Marketing AI MCP Server
 * This wrapper allows installation via: claude mcp add ipcom-ai npx ipcom-marketing-ai
 */

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

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
 * Start the OSP Marketing Tools MCP Server
 */
async function startServer() {
    try {
        console.log('🚀 Starting IPCOM Marketing AI MCP Server...');
        
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
                console.error(`❌ Server exited with code ${code}`);
                process.exit(code);
            }
        });
        
        server.on('error', (error) => {
            console.error('❌ Failed to start server:', error.message);
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
        process.exit(1);
    }
}

// Start the server
startServer();