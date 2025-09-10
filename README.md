# 🎨 Stable Diffusion MCP Server

[![License](https://img.shields.io/badge/License-Dual-blue.svg)](LICENSE.md)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-Compatible-orange.svg)](https://github.com/modelcontextprotocol)

An enhanced Model Context Protocol (MCP) server for Stable Diffusion, providing comprehensive AI art generation capabilities through a simple, intuitive interface.

## ✨ Features

### 🎯 Core AI Art Generation
- **Text-to-Image (txt2img)**: Generate images from text descriptions
- **Image-to-Image (img2img)**: Transform existing images with AI
- **Prompt Analysis**: Reverse-engineer prompts from images (interrogate)

### 🔧 Advanced Capabilities
- **Model Management**: List, switch, and manage SD models dynamically
- **LoRA Support**: Apply LoRA models for enhanced artistic effects
- **Smart Recommendations**: AI-driven model and parameter suggestions
- **Auto-Launch**: Automatic detection and startup of SD WebUI
- **Multi-language Support**: Works with Chinese and English prompts

### 🛠️ MCP Tools Available

| Tool Name | Description | Key Parameters |
|-----------|-------------|----------------|
| `generate_image` | Text-to-image generation | prompt, model, lora, dimensions |
| `img2img` | Image-to-image transformation | image_path, prompt, denoising_strength |
| `interrogate_image` | Extract prompts from images | image_path, model |
| `list_models` | List available SD models | - |
| `list_loras` | List available LoRA models | - |
| `switch_model` | Change current SD model | model_name |
| `check_sd_status` | Check SD WebUI status | - |
| `start_sd_webui` | Launch SD WebUI | - |

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Stable Diffusion WebUI (AUTOMATIC1111 or compatible)
- SD WebUI running on `http://127.0.0.1:7860` (default)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/hkhkkh/stable-diffusion-mcp-server.git
   cd stable-diffusion-mcp-server
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your SD WebUI path** (optional)
   Edit `sd_mcp_server.py` and update the `SD_LAUNCHER_PATH` variable to point to your SD WebUI executable.

4. **Start the MCP server**
   ```bash
   python sd_mcp_server.py
   ```

### Usage Examples

#### Basic Image Generation
```
Generate a cute cat sitting in a garden
Create a cyberpunk cityscape at night
```

#### Advanced Generation with Model/LoRA
```
Using realistic model, draw a portrait with lora:detailed_face:0.8
Generate anime style artwork using anything model
```

#### Image-to-Image
```
Transform this image: C:\path\to\image.jpg into anime style
Based on this photo, create a fantasy version
```

#### Model Management
```
List all available SD models
Switch to majicmix_v7 model
Show current model information
```

## 🎨 Supported Models

The server includes intelligent model recommendations based on content type:

- **Realistic Models**: majicmix (v2, v7), chilloutmix, realistic series
- **Anime Models**: anything, animevae, cartoon styles
- **Specialized Models**: Architecture, landscapes, portraits
- **LoRA Support**: Facial details, style enhancements, character-specific

## 📁 Project Structure

```
stable-diffusion-mcp-server/
├── sd_mcp_server.py          # Main MCP server
├── requirements.txt          # Python dependencies
├── generated_images/         # Output directory
├── demo_ai_prompt_writing.py # AI prompt enhancement demo
├── test_*.py                # Test scripts
└── docs/                    # Additional documentation
```

## 🔧 Configuration

### SD WebUI Settings
- Default API URL: `http://127.0.0.1:7860`
- Output directory: `generated_images/`
- Auto-launch support for Windows SD WebUI

### Model Database
The server includes a comprehensive model knowledge base for intelligent recommendations:
- Model strengths and weaknesses
- Optimal use cases
- Tag associations
- Quality ratings

## 🧪 Testing

Run the included test scripts to verify functionality:

```bash
python test_smart_generate.py    # Test smart generation
python test_current_model.py     # Test model info
python test_recommendations.py   # Test model recommendations
```

## 📖 Documentation

- [AI-Driven Features Guide](AI_DRIVEN_README.md)
- [Translation Integration](TRANSLATION_FIX_SUMMARY.md)
- [MCP Integration Guide](SD_MCP_GUIDE.md)

## 🤝 Contributing

Contributions are welcome! Please read the [LICENSE.md](LICENSE.md) for licensing terms.

### For Non-Commercial Use
- Fork the repository
- Create a feature branch
- Submit a pull request

### For Commercial Use
- Contact the author for commercial licensing
- Revenue sharing agreement required

## 📄 License

This project uses a **dual licensing model**:

- **Non-Commercial**: CC BY-NC-SA 4.0 (free for personal/educational use)
- **Commercial**: Custom license with revenue sharing requirement

See [LICENSE.md](LICENSE.md) for full details.

## 📞 Contact

- **Author**: Yang Haokang
- **GitHub**: [@hkhkkh](https://github.com/hkhkkh)
- **Email**: 0221123105@mail.imu.edu.cn

For commercial licensing inquiries, please open an issue or contact directly.

## 🌟 Acknowledgments

- Built on the Model Context Protocol (MCP)
- Compatible with AUTOMATIC1111 Stable Diffusion WebUI
- Inspired by the open-source AI art community

---

**Made with ❤️ for the AI art community**