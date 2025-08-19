# IPCOM Marketing AI - Zero-Config Marketing Tools 🚀

<div align="center">

![License](https://img.shields.io/badge/license-CC%20BY--SA%204.0-blue?style=flat-square)
![Version](https://img.shields.io/badge/version-0.4.0-brightgreen?style=flat-square)
![NPM](https://img.shields.io/npm/v/ipcom-marketing-ai?style=flat-square)
![Python](https://img.shields.io/badge/python-3.8%2B-blue?style=flat-square)
![MCP](https://img.shields.io/badge/MCP-compatible-green?style=flat-square)

**🎯 Interactive Buyer Persona Generator + Enterprise Marketing Frameworks**
_Zero configuration. Works everywhere. Bilingual support (EN/PT-BR)._

[**🎭 Try Demo Now**](#-instant-demo-no-setup) •
[**⚡ Quick Install**](#-quick-install-30-seconds) •
[**📚 Documentation**](#-complete-documentation)

</div>

---

## 🎨 What's New in v0.4.0

### 🗣️ **Natural Language Interface** (NEW!)

- 💬 **Use simple commands** - "criar uma persona para meu produto X"
- 🌐 **Auto-detect language** - Works in Portuguese or English
- 🎯 **Extract context** - Understands your product from description
- ⚡ **Instant start** - No need to specify parameters

### ✨ **Zero-Config Experience**

- 🚀 **Automatic MCP setup** - Works instantly with Claude Code
- 🎭 **Standalone demo mode** - Try without any configuration
- 🔧 **Smart auto-detection** - Finds and configures Claude Code automatically
- 📦 **Post-install automation** - Everything configured during npm install
- 🌍 **Works everywhere** - Windows, Mac, Linux support

### 🗣️ **Interactive Buyer Persona Generator**

- 🇺🇸 🇧🇷 **Bilingual support** - English and Portuguese Brazilian
- 🎯 **Adele Revella's 5 Rings** methodology
- 📊 **Quality scoring** with confidence metrics
- 🤖 **Smart interview engine** with dynamic questions
- 📈 **Market research integration**

---

## 🎭 Instant Demo (No Setup!)

Try the Interactive Buyer Persona Generator right now:

```bash
npx ipcom-marketing-ai demo
```

That's it! No installation, no configuration. Just works. 🎉

---

## ⚡ Quick Install (30 seconds)

### Option 1: NPM (Recommended)

```bash
# Install globally
npm install -g ipcom-marketing-ai

# Auto-configure for Claude Code
npx ipcom-marketing-ai configure

# Done! Restart Claude Code and tools are available
```

### Option 2: Claude Code Integration

```bash
# One command setup
claude mcp add ipcom-marketing-ai "npx ipcom-marketing-ai"
```

### Option 3: Manual MCP Config

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ipcom-marketing-ai": {
      "command": "npx",
      "args": ["ipcom-marketing-ai"]
    }
  }
}
```

---

## 🎯 Available Modes

### 1. **MCP Mode** (Claude Code)

Full integration with Claude Code - all tools available as native functions.

```bash
# Start MCP server
npx ipcom-marketing-ai

# Use in Claude Code:
"Create an interactive buyer persona in Portuguese"
```

### 2. **Standalone Mode** (CLI)

Interactive command-line experience without MCP.

```bash
# Run interactive demo
npx ipcom-marketing-ai demo
```

### 3. **Configuration Mode**

Automatic setup and troubleshooting.

```bash
# Configure MCP
npx ipcom-marketing-ai configure

# Check status
npx ipcom-marketing-ai status

# Get help
npx ipcom-marketing-ai help
```

---

## 🛠️ Core Features

### 🎭 **Interactive Buyer Persona Generator**

Create evidence-based buyer personas using Adele Revella's methodology:

- **5 Rings of Buying Insight**:
  - 🎯 Priority Initiative
  - ✅ Success Factors
  - 🚧 Perceived Barriers
  - 📊 Decision Criteria
  - 🗺️ Buyer's Journey

- **Bilingual Support**:
  - 🇺🇸 English - Full professional terminology
  - 🇧🇷 Portuguese Brazilian - Native localization

- **Quality Assurance**:
  - Confidence scoring (0-100%)
  - Cross-ring validation
  - Market research integration
  - Fallback data for reliability

### 📚 **Marketing Frameworks 2025**

8 cutting-edge methodologies for content excellence:

#### Marketing Content

- **IDEAL** - User-centered content creation
- **STEPPS** - Viral content framework
- **RACE** - Digital marketing planning
- **STP** - Segmentation, Targeting, Positioning

#### Technical Writing

- **GDocP** - Pharmaceutical-grade documentation
- **Docs-as-Code** - Version-controlled docs
- **Interactive Docs** - Dynamic documentation

#### SEO & Optimization

- **E-E-A-T** - Google's quality framework
- **Entity-Based SEO** - Semantic optimization
- **Topic Clusters** - Content organization

### ⚡ **Performance Features**

- **Batch Processing** - Analyze multiple contents in parallel
- **Advanced Caching** - TTL, persistence, smart invalidation
- **Priority Queue** - Process important content first
- **Real-time Progress** - Track batch operations
- **95%+ Test Coverage** - Enterprise-grade reliability

---

## 💡 Usage Examples

### Creating a Buyer Persona (Claude Code)

#### 🆕 Natural Language Mode (NEW!)

```python
# Just describe what you want in natural language!
use_marketing_ai("criar uma persona para meu produto de gestão financeira")
use_marketing_ai("create a persona for my SaaS that helps teams collaborate")
use_marketing_ai("gerar persona para minha consultoria de marketing digital")

# Or use quick start with just your product description
quick_start_persona("Meu app ajuda pequenas empresas com controle de estoque")
quick_start_persona("AI-powered code review tool for developers")

# Features:
# ✅ Auto-detects language (PT/EN)
# ✅ Extracts product context automatically
# ✅ Validates input (min 10 characters)
# ✅ Full error handling with helpful messages
```

#### Traditional Mode

```python
# Start interactive interview in English
create_interactive_persona(language="en")

# Start in Portuguese Brazilian
create_interactive_persona(language="pt-br")

# With product context
create_interactive_persona(
    product_context="SaaS project management tool",
    language="en"
)

# Continue the interview (after answering first question)
continue_persona_interview(
    session_id="your_session_id",
    response="Your answer to the question",
    language="pt-br"
)

# Check interview status
get_persona_interview_status(session_id="your_session_id")
```

### Standalone Demo

```bash
$ npx ipcom-marketing-ai demo

🎯 INTERACTIVE BUYER PERSONA GENERATOR - STANDALONE MODE
========================================================

📋 SELECT LANGUAGE / SELECIONE O IDIOMA:

  1. 🇺🇸 English (en)
  2. 🇧🇷 Português Brasileiro (pt-br)

Enter your choice (1-2): _
```

### Multi-Framework Analysis

```python
# Analyze content with all frameworks
analyze_content_multi_framework(
    content="Your marketing content here",
    frameworks=["IDEAL", "STEPPS", "E-E-A-T", "GDocP"]
)
```

### Batch Processing

```python
# Process multiple contents
analyze_content_batch(
    batch_id="content_audit_2025",
    content_items=[
        {"content": "Article 1", "frameworks": ["IDEAL", "E-E-A-T"]},
        {"content": "Article 2", "frameworks": ["STEPPS", "GDocP"]},
        {"content": "Article 3", "frameworks": ["IDEAL", "STEPPS"]}
    ],
    priority=1
)
```

---

## 🔧 Troubleshooting

### MCP Not Recognized?

```bash
# Solution 1: Auto-configure
npx ipcom-marketing-ai configure

# Solution 2: Use standalone mode
npx ipcom-marketing-ai demo

# Solution 3: Check status
npx ipcom-marketing-ai status
```

### Common Issues

| Problem                       | Solution                                                  |
| ----------------------------- | --------------------------------------------------------- |
| Tool not found in Claude Code | Run `npx ipcom-marketing-ai configure` and restart Claude |
| Python not found              | Install Python 3.8+ from python.org                       |
| Permission denied             | Use `npm install -g` with appropriate privileges          |
| MCP connection failed         | Check Claude Code is running                              |

### Getting Help

- 📧 **Support**: contato@openpartners.com.br
- 🐛 **Issues**:
  [GitHub Issues](https://github.com/fabiotheo/ipcom-marketing-ai/issues)
- 📚 **Docs**:
  [Full Documentation](https://github.com/fabiotheo/ipcom-marketing-ai/wiki)

---

## 📚 Complete Documentation

### Available Tools

| Tool                              | Description                | Key Features                                           |
| --------------------------------- | -------------------------- | ------------------------------------------------------ |
| `use_marketing_ai`                | Natural language interface | Auto-detect language, Extract context, Start interview |
| `quick_start_persona`             | Quick persona creation     | Auto language, Simple input, Fast start                |
| `create_interactive_persona`      | Buyer persona generator    | Bilingual, 5 Rings, Quality scoring                    |
| `analyze_content_multi_framework` | Multi-framework analysis   | IDEAL, STEPPS, E-E-A-T, GDocP                          |
| `analyze_content_batch`           | Batch processing           | Parallel, Priority queue                               |
| `get_marketing_frameworks_2025`   | Marketing methodologies    | IDEAL, STEPPS, RACE, STP                               |
| `get_technical_writing_2025`      | Technical documentation    | GDocP, Docs-as-Code                                    |
| `get_seo_frameworks_2025`         | SEO optimization           | E-E-A-T, Entity-Based                                  |
| `get_editing_codes`               | Content editing system     | Semantic editing codes                                 |
| `get_writing_guide`               | Writing methodology        | Technical writing guide                                |
| `get_meta_guide`                  | Meta information           | SEO metadata creation                                  |
| `get_value_map_positioning_guide` | Product positioning        | Value communication                                    |
| `get_on_page_seo_guide`           | SEO optimization           | On-page SEO guide                                      |
| `health_check`                    | System status              | Performance metrics                                    |

### Configuration Options

Environment variables for customization:

```bash
# Cache settings
CACHE_MAX_SIZE=100           # Maximum cache entries
CACHE_TTL_SECONDS=3600       # Cache time-to-live
CACHE_ENABLE_PERSISTENCE=true # Persist cache to disk

# Batch processing
BATCH_MAX_SIZE=50            # Max items per batch
BATCH_PARALLEL_WORKERS=4     # Concurrent workers
BATCH_TIMEOUT_SECONDS=300    # Batch timeout

# Analysis limits
MAX_ANALYSIS_CONTENT_LENGTH=100000  # Max content size
STRICT_FRAMEWORK_VALIDATION=false   # Strict validation

# Logging
LOG_LEVEL=INFO               # DEBUG, INFO, WARNING, ERROR
```

---

## 🚀 Roadmap

### Phase 1: UX & Accessibility ✅

- [x] Zero-config setup
- [x] Standalone demo mode
- [x] Bilingual support
- [x] Auto-configuration script
- [x] Enhanced error messages

### Phase 2: Framework Expansion (Q1 2025)

- [ ] Jobs-to-be-Done framework
- [ ] StoryBrand methodology
- [ ] Content Design System
- [ ] Accessibility frameworks

### Phase 3: AI Enhancement (Q2 2025)

- [ ] Custom persona templates
- [ ] Industry-specific models
- [ ] Competitive analysis
- [ ] Content suggestions

### Phase 4: Enterprise Features (Q3 2025)

- [ ] Team collaboration
- [ ] Export integrations
- [ ] API access
- [ ] Analytics dashboard

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone repository
git clone https://github.com/fabiotheo/ipcom-marketing-ai.git
cd ipcom-marketing-ai

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run demo
python demo_standalone.py
```

---

## 📄 License

**Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**

You are free to:

- ✅ **Share** - Copy and redistribute
- ✅ **Adapt** - Remix, transform, and build upon
- ✅ **Commercial** - Use for commercial purposes

Under the following terms:

- **Attribution** - Give appropriate credit
- **ShareAlike** - Distribute contributions under same license

---

## 🙏 Acknowledgments

- **Adele Revella** - Buyer Personas methodology
- **Open Strategy Partners** - Core methodologies
- **Anthropic** - Model Context Protocol
- **Community** - Feedback and contributions

---

<div align="center">

**Built with ❤️ by [IPCOM](https://ipcom.com.br) &
[Open Strategy Partners](https://openstrategypartners.com)**

[Report Bug](https://github.com/fabiotheo/ipcom-marketing-ai/issues) •
[Request Feature](https://github.com/fabiotheo/ipcom-marketing-ai/issues) •
[Documentation](https://github.com/fabiotheo/ipcom-marketing-ai/wiki)

</div>
