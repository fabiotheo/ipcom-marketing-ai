# IPCOM Marketing AI - NPM Wrapper

🚀 **NPM wrapper for IPCOM Marketing AI MCP Server**

This package provides a convenient NPM wrapper for the comprehensive OSP Marketing Tools suite, enabling easy installation and integration with Claude Desktop and Claude Code via the Model Context Protocol (MCP).

## ⚡ Quick Installation

### **For Claude Code (Recommended):**
```bash
# 1. Install globally
npm install -g ipcom-marketing-ai@latest

# 2. Add to Claude MCP
claude mcp add ipcom-marketing-ai ipcom-marketing-ai
```

### **Alternative Methods:**
```bash
# Global installation only
npm install -g ipcom-marketing-ai

# Direct execution (for testing)
npx ipcom-marketing-ai
```

> **Note:** Global installation is recommended for MCP integration as it ensures proper permissions and reliable connectivity.

## 🎯 What's Included

- **8 Modern Marketing Frameworks (2025)**: IDEAL, STEPPS, E-E-A-T, GDocP
- **Batch Processing System**: Parallel content analysis with configurable workers
- **Advanced Cache System**: TTL, persistence, tag invalidation
- **16 Professional Tools**: Content analysis, SEO optimization, value mapping
- **95%+ Test Coverage**: Enterprise-grade reliability
- **Comprehensive Documentation**: API reference, developer guides

## 🛠️ Features

### **Core OSP Methodologies**
- Product Value Map Generator
- Meta Information Generator  
- Content Editing Codes
- Technical Writing Guide
- On-Page SEO Guide

### **2025 Enhancement Frameworks**
- Marketing Frameworks 2025 (IDEAL, STEPPS, RACE, STP)
- Technical Writing 2025 (GDocP, Docs-as-Code)
- SEO Frameworks 2025 (E-E-A-T, Entity-Based SEO)

### **Advanced Analysis Tools**
- Multi-Framework Content Analysis
- Real-time Progress Tracking
- Parallel Batch Processing
- Intelligent Caching System

## 📋 Usage Examples

Once installed in Claude Desktop/Code, you can use commands like:

```
"Analyze this content using IDEAL framework: [your content]"
"Generate value map for my SaaS product using OSP methodology"  
"Apply E-E-A-T analysis to this technical documentation"
"Process these 10 blog posts using batch analysis with STEPPS framework"
```

## 🔧 Requirements

- **Node.js**: 18.0.0 or higher
- **Python**: 3.10+ (automatically installed via uv)
- **uv**: Automatically installed if not present

## 💡 Example Usage

After installation, you can analyze marketing content directly in Claude Code:

```
Analyze this marketing content using IDEAL, STEPPS, and E-E-A-T frameworks:

🚀 Transform your productivity with FlowDesk Pro!

Tired of wasting time on repetitive tasks? Our intelligent automation platform uses AI to automatically organize your emails, schedule meetings, and prioritize your most important tasks.

✅ Proven results: Our 50,000+ users report 70% less time wasted on administration
✅ Award-winning technology: Recognized by TechCrunch as 'Startup of the Year 2024'  
✅ Perfect integration: Works with Gmail, Outlook, Slack, Notion and 200+ tools

💡 Real testimonial: 'FlowDesk gave me back 3 hours per day. Now I can focus on what really matters for my business!' - Maria Silva, CEO of TechStart

🎯 Special offer: First 1000 users get 6 months FREE + personalized productivity consulting.

👉 Start free now - no credit card required

Join the productivity revolution. Your competitors are already ahead.
```

The analysis will provide detailed scores and recommendations for each framework, helping you optimize your marketing content.

## 📚 Documentation

- **Main Repository**: [ipcom-marketing-ai](https://github.com/fabiotheo/ipcom-marketing-ai)
- **Technical Documentation**: [docs/TECHNICAL_DOCUMENTATION.md](https://github.com/fabiotheo/ipcom-marketing-ai/blob/main/docs/TECHNICAL_DOCUMENTATION.md)
- **Developer Guide**: [docs/DEVELOPER_GUIDE.md](https://github.com/fabiotheo/ipcom-marketing-ai/blob/main/docs/DEVELOPER_GUIDE.md)
- **API Reference**: [docs/API_REFERENCE.md](https://github.com/fabiotheo/ipcom-marketing-ai/blob/main/docs/API_REFERENCE.md)

## 🏷️ Version Information

- **Version**: 0.3.3 (Phase 3 - Batch Processing & Advanced Cache + Improved MCP Integration)
- **Python Package**: Automatically fetched from GitHub
- **MCP Compatibility**: Full Model Context Protocol support
- **Claude Integration**: Native Claude Desktop and Claude Code support

## 🔧 Development & Publishing

### **Testing Locally**
```bash
# Test the wrapper locally
./test-local.sh
```

### **Publishing Updates**
```bash
# Automated publication process
./publish.sh
```

### **Manual Process**
```bash
# Update version
npm version patch|minor|major

# Test locally
npm pack && node index.js

# Publish to NPM
npm publish
```

## 📚 Complete Publication Guide

See [NPM_PUBLICATION_GUIDE.md](../docs/NPM_PUBLICATION_GUIDE.md) for detailed instructions on publishing and updating this package.

## 🤝 Contributing

This NPM wrapper is part of the larger IPCOM Marketing AI project. Contributions welcome!

1. **Main Project**: [ipcom-marketing-ai](https://github.com/fabiotheo/ipcom-marketing-ai)
2. **Report Issues**: [GitHub Issues](https://github.com/fabiotheo/ipcom-marketing-ai/issues)
3. **Feature Requests**: [GitHub Discussions](https://github.com/fabiotheo/ipcom-marketing-ai/discussions)

## 📄 License

This project is licensed under CC BY-SA 4.0 - see the main repository for details.

## 🙏 Attribution

Based on methodologies from [Open Strategy Partners](https://openstrategypartners.com).

---

**Made with ❤️ by the IPCOM & OSP Community**

*Enhanced with 2025 Frameworks • Professional Grade • Community Driven*