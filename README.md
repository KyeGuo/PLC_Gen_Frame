# PLC 代码自动生成框架

基于 DeerFlow 多智能体协作的 TwinCAT PLC 代码自动生成框架。

## 📋 目录

- [项目概述](#项目概述)
- [架构设计](#架构设计)
- [快速开始](#快速开始)
- [使用指南](#使用指南)
- [技术文档](#技术文档)

## 项目概述

本框架通过多智能体协作，实现 PLC 代码的自动生成、验证和优化。用户只需提供功能需求，系统会自动完成从方案设计到最终可执行代码的全流程。

### 主要特性

- ✅ **多智能体协作**：5个专业智能体协同工作
- ✅ **自动化流程**：从需求到代码的全流程自动化
- ✅ **TwinCAT 集成**：内置 TwinCAT MCP 工具验证
- ✅ **可视化交互**：完整的 Web 界面和流程可视化
- ✅ **可扩展性**：支持自定义智能体和工具

## 架构设计

### 智能体体系

| 智能体 | 角色 | 职责 |
|--------|------|------|
| **plc-coordinator** | 总协调智能体 | 协调整个流程，调用子智能体 |
| **plc-designer** | 方案设计智能体 | 设计 PLC 架构、功能块和数据结构 |
| **plc-coder** | 代码编写智能体 | 生成符合 TwinCAT 规范的代码文件 |
| **plc-validator** | 代码验证智能体 | 使用 TwinCAT MCP 工具验证代码 |
| **plc-optimizer** | 代码优化智能体 | 修复和优化 PLC 代码 |

### 工作流程

```
用户需求
    ↓
需求分析 (plc-coordinator)
    ↓
方案设计 (plc-designer)
    ↓
代码生成 (plc-coder)
    ↓
代码验证 (plc-validator)
    ↓
通过？ → 否 → 代码优化 (plc-optimizer) → 回到验证
    ↓ 是
交付最终代码
```

## 快速开始

### 前置要求

- Python 3.12+
- Node.js 18+
- Git
- uv (Python 包管理器，用于 monorepo 管理)

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/KyeGuo/PLC_Gen_Frame.git
cd PLC_Gen_Frame
```

2. **安装 uv (如果尚未安装)**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# 或使用 pip: pip install uv
```

3. **创建并激活虚拟环境**
```bash
cd backend
uv venv
source .venv/bin/activate  # Linux/Mac
# 或在 Windows 上使用: .venv\Scripts\activate
```

4. **安装后端依赖**
```bash
uv pip install -e .
```

5. **安装 Agents4PLC 基准测试数据集**

本框架使用 Agents4PLC_release 作为基准测试数据集。需要将其克隆到项目同级目录：

```bash
cd ..
git clone https://github.com/Luoji-zju/Agents4PLC_release.git
cd PLC_Gen_Frame/backend
```

数据集目录结构要求：
```
Project/
├── PLC_Gen_Frame/           # 本框架
└── Agents4PLC_release/  # 基准测试数据集（必须在此位置）
    ├── benchmark_v2/    # 包含 medium.jsonl, hard.jsonl, high-fidelity.jsonl
    ├── api/             # API 接口定义
    ├── server.py        # 基准测试服务
    └── ...
```

6. **安装 TwinCAT Validator MCP 工具**
```bash
# 假设 twincat-validator-mcp 在同级目录
cd ..
git clone https://github.com/your-org/twincat-validator-mcp.git
cd twincat-validator-mcp
uv pip install -e .
cd ../PLC_Gen_Frame/backend
```

7. **安装前端依赖**
```bash
cd ../../frontend
npm install
```

8. **配置环境**

首先创建 PLC 工作空间目录：
```bash
mkdir -p ../plc-workspace
```

然后配置 `extensions_config.json`（路径相对于 backend 目录）：
```json
{
  "mcpServers": {
    "twincat-validator": {
      "enabled": true,
      "type": "stdio",
      "command": ".venv/bin/python",
      "args": [
        "-m",
        "twincat_validator"
      ],
      "env": {},
      "description": "TwinCAT 3 PLC代码验证、自动修复和脚手架工具"
    },
    "filesystem": {
      "enabled": true,
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "../../plc-workspace"
      ],
      "env": {},
      "description": "文件系统访问，用于读写PLC代码文件"
    }
  },
  "skills": {}
}
```

**注意**：配置文件中的路径是相对于 backend 目录的，因为服务是从 backend 目录启动的。

### 验证 TwinCAT MCP 部署

在启动服务之前，建议验证 TwinCAT Validator MCP 是否正确安装：

```bash
cd backend
source .venv/bin/activate

# 验证 MCP 命令
.venv/bin/twincat-validator-mcp --help
```

**预期输出：**
```
Starting twincat-validator v1.0.0
Supported file types: .TcPOU, .TcIO, .TcDUT, .TcGVL
Validation checks: 45
Auto-fix capabilities: 10
Server ready to accept connections
```

如果看到错误信息，请检查：
1. 是否已正确安装 twincat-validator-mcp
2. Python 虚拟环境是否正确激活

### 配置 API Key

在启动服务之前，您需要配置 LLM 模型的 API Key。框架支持多种模型提供商：

1. **设置环境变量**

   ```bash
   # 使用 OpenAI（推荐）
   export OPENAI_API_KEY="your-openai-api-key"
   
   # 或者使用其他模型
   # export VOLCENGINE_API_KEY="your-volcengine-api-key"
   # export ANTHROPIC_API_KEY="your-anthropic-api-key"
   # export GOOGLE_API_KEY="your-google-api-key"
   ```

2. **配置模型**

   编辑 `config.yaml` 文件，取消注释并配置您想要使用的模型：

   ```yaml
   models:
     - name: gpt-4
       display_name: GPT-4
       use: langchain_openai:ChatOpenAI
       model: gpt-4
       api_key: $OPENAI_API_KEY
       request_timeout: 600.0
   ```

   **支持的模型：**
   - OpenAI (GPT-4, GPT-3.5)
   - Anthropic (Claude 3.5)
   - Google Gemini
   - Volcengine (Doubao)
   - DeepSeek
   - Moonshot (Kimi)
   - Ollama (本地模型)

### 启动服务

#### 方式一：使用启动脚本（推荐）

```bash
# 启动所有服务
./start.sh

# 停止所有服务
./stop.sh
```

#### 方式二：手动启动

1. **启动后端服务**
```bash
cd backend
source .venv/bin/activate
make dev
```

2. **启动前端服务**（新开一个终端）
```bash
cd frontend
npm run dev
```

3. **启动基准测试服务**（新开一个终端）
```bash
cd ../Agents4PLC_release
python server.py
```

4. **访问应用**
- 前端地址：http://localhost:3000
- 后端 API：http://localhost:8001
- 基准测试 API：http://localhost:5000

## 使用指南

### 生成 PLC 代码

1. **打开应用**
   - 访问 http://localhost:3000

2. **选择智能体**
   - 点击"开始使用"进入智能体选择页面
   - 选择"总协调智能体"

3. **描述需求**
   - 在对话界面中描述您的 PLC 需求
   - 例如："创建一个电机控制功能块，支持启停、正反转和速度调节"

4. **等待生成**
   - 系统会自动调用各个智能体完成任务
   - 您可以在界面上看到每个步骤的进度

5. **获取结果**
   - 生成完成后，代码文件会保存在 `../plc-workspace` 目录（或你在 extensions_config.json 中配置的路径）
   - 文件格式包括：`.TcPOU`、`.TcDUT`、`.TcGVL` 等

### 需求描述示例

**基础需求：**
```
创建一个简单的电机控制功能块
- 输入：启动、停止、正转、反转
- 输出：电机运行状态、运行方向
```

**高级需求：**
```
创建一个完整的电机控制系统
- 功能：
  * 启停控制
  * 正反转切换
  * 0-100% 速度调节
- 保护功能：
  * 过流保护
  * 过热保护
  * 过载保护
- 诊断功能：
  * 故障历史记录
  * 实时状态监控
```

## 技术文档

详细的技术文档请参考：
- [技术报告](./docs/TECHNICAL_REPORT.md)
- [测试验证方案](./docs/TEST_PLAN.md)
- [测试报告](./docs/TEST_REPORT.md)

## 项目结构

```
PLC_Gen_Frame/
├── start.sh                  # 启动脚本
├── stop.sh                   # 停止脚本
├── README.md                 # 项目说明
├── config.yaml               # 配置文件
├── extensions_config.json    # MCP 扩展配置
├── backend/                  # 后端服务
│   ├── .PLC_Gen_Frame/agents/    # 智能体定义
│   ├── app/                  # FastAPI 应用
│   └── packages/             # 核心包
├── frontend/                 # 前端应用
│   └── src/                  # 源代码
└── docs/                     # 文档目录
    ├── TECHNICAL_REPORT.md
    ├── TEST_PLAN.md
    └── TEST_REPORT.md
```

## 许可证

本项目基于 DeerFlow 框架开发。
