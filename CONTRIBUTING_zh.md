# 贡献指南

感谢您对 I.R.I.S. 智能终端项目的兴趣！我们欢迎各种形式的贡献，包括但不限于：
- 🐛 Bug 修复
- ✨ 新功能
- 📚 文档改进
- 🎨 代码优化
- 🧪 测试完善

## 开发环境设置

### 1. Fork 项目

点击 GitHub 页面的 `Fork` 按钮，创建您自己的仓库副本。

### 2. 克隆您的仓库

```bash
git clone https://github.com/YOUR_USERNAME/Wuthering-Waves-I.R.I.S.-Smart-Terminal.git
cd Wuthering-Waves-I.R.I.S.-Smart-Terminal
```

### 3. 添加上游仓库

```bash
git remote add upstream https://github.com/YarXVI/Wuthering-Waves-I.R.I.S.-Smart-Terminal.git
```

### 4. 创建开发分支

```bash
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/your-bug-fix-name
```

## 开发流程

### 后端开发

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r agent_core/requirements.txt

# 运行开发服务器
python -m server.main

# 运行测试
python -m pytest tests/ -v
```

### 前端开发

```bash
cd desktop

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 运行测试
npm test
```

## 代码规范

### Python（后端）

- 遵循 PEP 8 风格指南
- 为函数参数和返回值使用类型提示
- 为所有公共函数和类编写文档字符串
- 保持函数小而专注（单一职责原则）

示例：

```python
def greet_user(name: str, age: int) -> str:
    """为用户生成问候消息。

    参数:
        name: 用户名
        age: 用户年龄

    返回:
        问候字符串
    """
    return f"你好，{name}！你 {age} 岁了。"
```

### TypeScript/React（前端）

- 遵循 ESLint 和 Prettier 配置
- 使用带 hooks 的函数式组件
- 使用 PropTypes 或 TypeScript 接口定义组件属性
- 保持组件小而可复用

示例：

```typescript
interface GreetingProps {
  name: string;
  age: number;
}

export const Greeting: React.FC<GreetingProps> = ({ name, age }) => {
  return <div>你好，{name}！你 {age} 岁了。</div>;
};
```

## 提交规范

请遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <subject>

[可选 body]

[可选 footer]
```

### 类型标识

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档变更
- `style`: 代码格式（不影响功能）
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具相关

### 示例

```
feat(chat): 添加消息持久化功能
fix(agent): 解决 AgentManager 中的线程安全问题
docs(readme): 更新安装说明
```

## Pull Request 流程

### 1. 保持分支更新

在提交 PR 之前，确保您的分支与上游同步：

```bash
git fetch upstream
git merge upstream/main
```

### 2. 运行测试

确保所有测试通过后再提交：

```bash
# 后端测试
python -m pytest tests/ -v

# 前端测试
cd desktop && npm test
```

### 3. 提交 Pull Request

- 使用清晰描述性的标题
- 详细描述变更内容
- 关联相关 issue
- 请求维护者审核

### 4. 处理反馈

- 及时回复审核意见
- 必要时进行修改并推送更新

## 问题报告

报告问题时，请包含：

- **问题标题**：清晰且具有描述性
- **描述**：详细说明问题
- **复现步骤**：如何复现问题
- **预期行为**：应该发生什么
- **实际行为**：实际发生了什么
- **环境**：操作系统、Python/Node 版本等
- **截图**：如适用

## 问题？

如有任何问题，您可以：
- 提交 issue 进行讨论
- 加入社区讨论
- 直接联系维护者

感谢您对 I.R.I.S. 智能终端项目的贡献！
