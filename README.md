# 机会灯塔 Skill

让 Codex、OpenClaw、Claude Code 等 Agent 用一句自然语言，通过[机会灯塔](https://job-lighthouse.godcorn001.workers.dev)搜索多家公司公开岗位。

它会把职位名称当作线索，而不是边界：先宽松找到职责相近的岗位，再展示匹配理由、原文证据和潜在风险。平台的抓取器、数据库与排序服务保持私有；本仓库只开源透明、可修改的 Agent 客户端。

## 安装

Codex：

```bash
git clone https://github.com/YUHAO-corn/job-lighthouse-skill.git ~/.codex/skills/job-lighthouse-skill
```

其他支持 `SKILL.md` 的 Agent，可把仓库克隆到其 skills 目录。也可以直接运行零依赖客户端：

```bash
python3 scripts/job_lighthouse.py search "上海或杭州，AI 与游戏相关，偏创作者工具，不要纯销售" --json
```

## 隐私

搜索时，你的求职需求会发送给机会灯塔 API，才能完成远程检索。请不要在查询里附带手机号、简历全文或公司机密。

客户端默认记录一次匿名安装量和汇总调用量，不发送搜索句子、岗位、账号或设备指纹。你可以随时关闭：

```bash
python3 scripts/job_lighthouse.py telemetry off
```

也可设置 `JOB_LIGHTHOUSE_TELEMETRY=0`。代码完全公开，欢迎检查或删除统计逻辑。

## 自托管兼容

若你有兼容的 API：

```bash
export JOB_LIGHTHOUSE_API_URL=https://your-domain.example/api
```

详见 [SKILL.md](./SKILL.md) 和 [API 文档](./references/api.md)。

## License

MIT
