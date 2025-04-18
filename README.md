# 微信读书 MCP 服务

微信读书 MCP（Multi-agent Collaboration Protocol）服务允许 AI 代理与您的微信读书库进行交互，帮助您更好地管理和分析您的阅读内容。

## 功能特点

- 检索您微信读书库中的图书
- 获取详细的图书信息
- 获取您的划线和书签
- 访问章节信息
- 查看阅读进度
- 获取书评和笔记
- 格式化划线以便分享

## 设置

### 前提条件

1. Python 3.7+
2. 一个有效的微信读书账号及 Cookie

### 安装

1. 克隆此仓库:
   ```
   git clone https://github.com/aixiasang/weread-mcp.git
   cd weread-mcp
   ```

2. 安装依赖:
   ```
   pip install -r requirements.txt
   ```

3. 设置您的微信读书 Cookie:
   - 在项目根目录创建一个 `.env` 文件
   - 添加您的微信读书 Cookie: `WEREAD_COOKIE="your_cookie_string_here"`

### 运行服务器

运行服务器:

```bash
python server.py
```

服务器默认将在 http://localhost:8000 上可用。

## 使用 MCP

### MCP 配置示例

在 Cursor 中，您可以通过以下配置使用微信读书 MCP：

```json
{
  "mcpServers": {
    "weread": {
      "command": "python",
      "args": [
        "/path/to/your/weread-mcp/server.py"
      ],
      "env": {
        "WEREAD_COOKIE": "your_weread_cookie_here",
        "PORT": "8000"
      }
    }
  }
}
```

设置好 `WEREAD_COOKIE` 环境变量后，所有 MCP 工具调用将自动使用此 Cookie，无需在每次调用时提供。服务启动时会创建一个持久的客户端实例，提高性能和可靠性。

### 使用 FastMCP 客户端

您可以使用 FastMCP 客户端与 MCP 服务器交互:

```python
from fastmcp.client import FastMCPClient

# 创建客户端
client = FastMCPClient("http://localhost:8000")

# 获取您库中的所有书籍
books = await client.call_tool("get_books")

# 获取特定书籍的信息
book_info = await client.call_tool("get_book_info", {"book_id": "book12345"})

# 获取书籍的划线
bookmarks = await client.call_tool("get_book_bookmarks", {"book_id": "book12345"})
```

## FastAPI 接口

本项目还提供了基于 FastAPI 的 REST API 接口，可以通过以下命令启动:

```bash
python api_server.py
```

这将启动一个与 MCP 服务器提供相同功能的 FastAPI 服务器。

## 可用工具

- `authenticate(cookie: str)`: 测试您的微信读书 Cookie 是否有效
- `get_books()`: 获取您微信读书库中的所有书籍
- `get_book_info(book_id: str)`: 获取特定书籍的详细信息
- `get_book_bookmarks(book_id: str)`: 获取特定书籍的划线/书签
- `get_book_chapters(book_id: str)`: 获取特定书籍的章节信息
- `get_book_read_info(book_id: str)`: 获取特定书籍的阅读进度和信息
- `get_book_reviews(book_id: str)`: 获取特定书籍的评论和笔记
- `get_web_url(book_id: str)`: 获取特定书籍的微信读书网页链接
- `format_book_highlights(book_id: str, max_highlights?: int)`: 将书籍划线格式化为 markdown 字符串
- `search_books(query: str)`: 通过标题或作者搜索您微信读书库中的书籍

## 身份验证

所有工具都使用环境变量中配置的 `WEREAD_COOKIE` 进行身份验证，您只需要：

1. 在 `.env` 文件中设置 `WEREAD_COOKIE` 环境变量
2. 或在启动服务器时通过环境变量传入

这样一次配置后，所有后续的调用都会自动使用该 Cookie，简化了使用流程。

## 免责声明

**本项目仅供个人学习使用。请尊重微信读书的用户协议和版权规定。不得将本工具用于任何商业目的或侵犯版权的行为。**

## 许可证

MIT 