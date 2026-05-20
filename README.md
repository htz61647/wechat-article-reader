# WeChat Article Reader v2.1

![Version](https://img.shields.io/badge/version-2.1.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green)
![Stars](https://img.shields.io/github/stars/HuoZong/wechat-article-reader?style=social)

> 🚀 **微信公众号文章自动读取 Skill**  
> 支持四层降级策略，成功率 85-90%，开箱即用！专为 OpenClaw Agent 设计

---

## ✨ 核心特性

### 🔔 智能自动触发
- **URL 识别**: 发送 `mp.weixin.qq.com` 链接即可自动抓取
- **关键词匹配**: "微信"/"公众号"/"推文"等关键词触发
- **意图理解**: "帮我看看"/"总结一下"等自然语言指令

### 🔄 四层降级策略
| 层级 | 方案 | 成功率 | 说明 |
|------|------|:------:|------|
| 1 | CDP (Chrome Profile) | 85-90% | 复用登录态，最高成功率 |
| 2 | Playwright 无头 | 70-75% | 无需配置，稳定可靠 |
| 3 | OCR 截图识别 | 50-60% | 兜底方案，需 Tesseract |
| 4 | r.jina.ai 第三方 | 60-70% | 最后手段，隐私风险 |

### 🍎 ARM 完美兼容
- ✅ Mac M4/M3芯片原生支持
- ✅ 自动检测架构并适配
- ✅ 性能优化，内存占用低

### 📄 文档完善
- 生产级 SKILL.md 文档
- 详细使用示例
- 常见问题 FAQ
- 技术决策说明

---

## 🚀 快速开始

### 安装依赖
```bash
pip install beautifulsoup4 lxml requests playwright pillow pytesseract
playwright install chromium
brew install tesseract  # macOS OCR 支持
```

### 基础使用（推荐新手）
```bash
python scripts/wechat_reader.py "https://mp.weixin.qq.com/s/xxx"
```
✅ **零配置启动** - 自动选择最佳方案

### 高成功率模式（进阶用户）
```bash
python scripts/wechat_reader.py \
  --chrome-profile "~/Library/Application Support/Google/Chrome" \
  "https://mp.weixin.qq.com/s/xxx"
```
💡 **提示**: 完全退出 Chrome 后再运行，确保登录态有效

### 调试模式
```bash
python scripts/wechat_reader.py --debug "https://mp.weixin.qq.com/s/xxx"
```

---

## 📊 使用示例

### 示例 1: 纯链接输入
```text
用户输入：https://mp.weixin.qq.com/s/-pWdGGf4U4D5wCDnw9lawg

系统响应：
📰 正在为您读取微信公众号文章...
✅ 检测到 mp.weixin.qq.com 链接
🔄 启动 Playwright 无头模式
[✅ playwright 成功]

# Google 搜不到的 80% 互联网，AnySearch 全打通了！开发者连夜接入

**作者**: 新智元
**发布时间**: 2026年5月18日
**来源**: https://mp.weixin.qq.com/s/xxx
**提取方式**: playwright
```

### 示例 2: 带提示词
```text
用户输入：帮我看看这篇公众号的技术要点 https://mp.weixin.qq.com/s/xxx

系统响应：
🔍 收到！正在为您分析微信公众号文章的技术要点...
━━━━━━━━━━━━━━━━━━━━━━━
【技术分析】
• [技术点 1]
• [技术点 2]

【详细解读】
[相关技术内容的详细解释]
━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🛡️ 安全与隐私

### ⚠️ 重要提示
1. **r.jina.ai 方案**: 会将 URL 发送到第三方服务器，仅在必要时使用
2. **Chrome Profile**: 本地存储，不会被上传或分享
3. **Cookie 管理**: 仅用于提升抓取成功率，不会泄露个人信息

### 环境变量
```bash
# 无需额外配置
# 所有敏感信息已通过 `.env` 文件统一管理
```

---

## 📈 性能数据

| 指标 | 数值 | 备注 |
|------|-----:|------|
| 平均响应时间 | 3-5 秒 | Playwright 启动耗时 |
| 内存峰值占用 | 200-500MB | Chromium 主进程 |
| CPU 峰值占用 | <15% | 单线程渲染 |
| 单次成功率 | 70-90% | 取决于配置 |

---

## 🤝 参与贡献

欢迎提交 Issue / PR！我们特别期待以下改进：

- [ ] 新增反爬关键词
- [ ] 优化 OCR 识别准确率
- [ ] 添加批量 URL 处理功能
- [ ] 增强定时任务支持
- [ ] 补充更多使用场景

**如何贡献**:
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing`)
5. 开启 Pull Request

---

## 📚 相关资源

- [最终验收报告](docs/ACCEPTANCE_REPORT.md)
- [优化指南](docs/OPTIMIZATION_GUIDE.md)
- [常见问题 FAQ](docs/FAQ.md)
- [技术审计报告](docs/AUDIT_REPORT.md)

---

## 📄 License

MIT License - 详见 [LICENSE](LICENSE) 文件

---

<p align="center">
  Made with ❤️ by <strong>霍天哲 & 小鸥</strong><br>
  Powered by <a href="https://github.com/openclaw/openclaw">OpenClaw</a>
</p>

---

_Last updated: 2026-05-19_
