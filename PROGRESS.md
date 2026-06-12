# 开发进度

## 护城河① 多租户隔离 —— ✅ 完成（已验证）

- [x] 多租户数据模型：`tenant` / `users` / `document`，每张带 `tenant_id`，UUID 主键，`users(tenant_id,email)` 组合唯一
- [x] 三张表开启 RLS，`tenant_isolation` 策略按会话变量 `app.current_tenant` 过滤
- [x] 职责分离：应用用最小权限角色 `alice` 连库（受 RLS 约束）；迁移用 owner `maxaa`（可改表结构、绕过 RLS）
- [x] 每请求事务内 `set_config('app.current_tenant', tid, is_local=true)` 设租户上下文（池化安全，避免 SET 残留串租户）
- [x] fail-closed：无租户身份 → `current_setting(...,true)` 返回 NULL → 返回空
- [x] **读 + 写**双向隔离：跨租户 SELECT 看不到、跨租户 INSERT 被拒（省略 WITH CHECK 时 USING 同时作用于写入）
- [x] RLS 策略纳入 Alembic 迁移（`8c92134eadae`），可复现、可回滚（down/up roundtrip 验证过）
- [x] 自动化对抗性测试：`tests/test_db.py`，断言"只见己方、绝无他方"，含非空校验避免"假通过"

## 遗留项 / 技术债（推迟，但必须盯住）

- [x] ~~**🔴 安全关键**：租户来自未认证的 `X-Tenant-Id` 请求头~~ —— **已解决**：租户现在从 JWT（登录时签发、不可伪造）解析，`X-Tenant-Id` 头已彻底失效（验证：带 token + 伪造头仍只见自身数据）。
- [ ] `/health/document` 是临时测试接口（挂在 health 路由下），仅为验证 RLS。后续应改成正式的文档 API（独立路由 `/documents`）。
- [ ] 测试依赖手动种子数据（doc-a / doc-b）。后续改为：专用测试库 + fixture 自造数据 + 用完回滚，做到自包含、可在干净 CI 库上跑。
- [ ] 测试里 `engine.dispose()` 是规避"事件循环跨用"的权宜之计。后续升级为测试专用 `NullPool` 引擎 + `app.dependency_overrides` 覆盖 `get_db`。
- [ ] RLS policy 目前只显式写了 `USING`（靠省略时 USING 兜底写入校验）。如需更清晰，可显式补 `WITH CHECK`。

## 认证模块 —— ✅ 完成

- [x] 密码哈希：bcrypt（加盐 + cost，`hash_password` / `verify_password`）
- [x] 注册接口 `POST /auth/register`：建租户 + 首用户，事务原子，bcrypt 存哈希
- [x] 登录接口 `POST /auth/login`：验密码 → 签发 access + refresh JWT，防用户枚举（统一错误）
- [x] JWT 工具：HS256，secret 从 .env，access/refresh 分寿命，含 `sub`/`tenant_id`/`exp`/`type`
- [x] 认证依赖 `get_current_claims`：HTTPBearer 取 token → 验签 → 校验 `type=="access"`
- [x] protected 接口从 token 取 tenant_id 设 RLS 上下文（替换 X-Tenant-Id，🔴 已关闭）
- [x] refresh 接口 `POST /auth/refresh`：refresh token 换新 access，校验 type==refresh，错误信息按场景准确

- [x] DRY 重构：`get_tenant_db` 依赖（封装"认证→设租户→yield session"），protected 接口只管查询；旧 `get_db` 退休
- [x] 异常处理加固：`get_current_claims` fail-closed——畸形 token（缺字段/错 type/过期/坏签名/乱码）全部 401，无 500（已对抗测试 + 日志确认无 traceback）

### 认证遗留项

- [ ] 全局异常处理器（`@app.exception_handler`）兜意外 500，不泄露堆栈——生产化，护城河做完统一加
- [ ] 注册"加入已有租户"时需捕获 `IntegrityError` → 409（当前每次新建租户，暂不触发）
- [ ] 登录用 tenant_id（UUID）——已知 UX 问题，生产用子域名/slug 解析，当前由客户端携带（见对话决策"保持 A"）

## 下一步候选

- 认证收尾：2.5 refresh 接口 + `get_tenant_db` DRY 重构
- 或进入护城河②（混合检索 + 重排）/ 护城河③（Redis 分布式锁与限流）
