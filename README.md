# OpenClaw 外贸数字员工（MVP骨架）

## 目录
- `kb-templates/`: 三个知识库 CSV 模板（已含 20 条英文示例）
- `skills/`: 三个 skill system prompt
- `routing/`: 路由和风控规则
- `data/`: 历史对话回放样例
- `scripts/`: 回放评估脚本
- `app/`: 本地网页聊天入口与 `/chat` API
- `docs/`: 架构与实施清单

## 快速开始
1. 把公司真实资料替换 `kb-templates/*.csv` 示例内容。
2. 将 `skills/*.md` 导入 OpenClaw 对应 skill。
3. 按 `routing/router-rules.yaml` 配置意图路由。
4. 运行回放评估：

```bash
python scripts/replay_eval.py
```

5. 运行多意图合并评估：

```bash
python scripts/multi_intent_eval.py
```

6. 启动本地聊天 Demo：

```bash
python app/server.py
```

打开 `http://127.0.0.1:8787` 即可测试。

7. 一键启动 WhatsApp 联调（Server + ngrok）：
```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_whatsapp_dev.ps1
```
脚本会输出可粘贴到 Meta 的 webhook 地址。

## API 调试
- `POST /chat`
```json
{"message":"Please share M8 spec and MOQ"}
```

- `POST /webhook/whatsapp`
```json
{"from":"+123456","message":"Your price is too expensive"}
```

- `GET /webhook/whatsapp`（Meta 验证）
  - 参数：`hub.mode` `hub.verify_token` `hub.challenge`
- `POST /webhook/whatsapp`（支持 Meta Cloud API payload）
  - 默认 `WHATSAPP_AUTO_REPLY=0`：只返回回复预览，不实际发消息
  - 开启 `WHATSAPP_AUTO_REPLY=1` 且配置完整后：会自动调用 Meta API 回发到手机端

- `GET /webhook/wecom`（企业微信签名验证）
  - 参数：`signature` `timestamp` `nonce` `echostr`
- `POST /webhook/wecom`（MVP JSON 结构）
```json
{"from":"u001","message":"Please share MOQ"}
```

## 渠道配置
环境变量：
- `WHATSAPP_VERIFY_TOKEN`
- `WHATSAPP_ACCESS_TOKEN`
- `WHATSAPP_PHONE_NUMBER_ID`
- `WHATSAPP_GRAPH_VERSION`
- `WHATSAPP_AUTO_REPLY`
- `WECOM_TOKEN`

可参考 [.env.example](C:\Users\31072\openclaw-trade-employee\.env.example)。
项目支持自动读取根目录 `.env`，不需要手动 `set` 环境变量。

如果终端 `python` 命中 WindowsApps 占位程序，请用实际路径：
`C:\\Users\\31072\\AppData\\Local\\Programs\\Python\\Python310\\python.exe`

## 建议指标
- 首响时间（FRT）
- 有效线索率
- 报价转化率
- 转人工率
- 幻觉率（错误事实回复率）
