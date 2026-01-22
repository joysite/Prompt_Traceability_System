# 农产品二维码溯源系统（MVP）

一个基于 **FastAPI + SQLite** 的轻量级农产品溯源系统，提供：

- B 端后台：批次管理、克隆批次、录入溯源信息（Vue 3 + Element Plus）。
- C 端 H5：扫码查看溯源详情与软防伪提示（Vue 3 + Vant + TailwindCSS）。
- 后端：批次 CRUD、扫码统计、防伪逻辑、JWT 管理员登录。

---

## 1. 目录结构

```bash
Prompt_Traceability_System/
├── backend/                  # FastAPI 后端
│   ├── main.py               # 应用入口
│   ├── models.py             # SQLAlchemy 模型 & DB
│   ├── routers/
│   │   ├── auth.py           # 登录 & JWT
│   │   ├── trace.py          # C 端溯源接口（扫码）
│   │   └── batch_admin.py    # B 端批次 CRUD & 克隆
│   └── __init__.py
│
├── frontend/
│   ├── h5/                   # C 端 H5（Vite + Vue 3 + Vant + Tailwind）
│   └── admin/                # B 端管理后台（Vite + Vue 3 + Element Plus + Tailwind）
│
├── init_batch.py             # 示例批次数据初始化脚本
├── administrater.py          # 管理员账号初始化脚本（可选）
├── requirements.txt          # 后端依赖
└── README.md
```

---

## 2. 后端环境与启动

### 2.1 安装依赖

在项目根目录：

```bash
pip install -r requirements.txt
```

### 2.2 启动 FastAPI 服务

```bash
uvicorn backend.main:app --reload
```

默认地址：<http://127.0.0.1:8000>

> 提示：启动时可能看到 Pydantic 关于 `orm_mode` 的 warning，可忽略，不影响运行。

---

## 3. 初始化管理员账号

使用脚本 `administrater.py`（或你自己的脚本）在 SQLite 中创建一个管理员账号。

示例逻辑（已经在 `administrater.py` 中）：

```python
from backend.models import SessionLocal, User, UserRole
from backend.routers.auth import get_password_hash

db = SessionLocal()

username = "admin"
plain_password = "123123"  # 登录时输入此明文密码

existing = db.query(User).filter(User.username == username).first()
if existing:
    print("user already exists:", existing.username)
else:
    user = User(
        username=username,
        password_hash=get_password_hash(plain_password),
        role=UserRole.ADMIN,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print("created admin:", user.id, user.username)
```

运行方式（在项目根目录）：

```bash
python administrater.py
```

---

## 4. 初始化示例批次数据

脚本 `init_batch.py` 会往 `batches` 表中插入一条测试批次：

- `batch_id = "TEST-20250101"`
- 包含产地信息、生产过程、物流标准、质检信息等 JSON 字段。

在项目根目录运行：

```bash
python init_batch.py
```

成功后终端会输出：

```text
created batch: TEST-20250101 id: 1
```

后台列表和 H5 溯源页面都可以用这条批次进行联调验证。

---

## 5. 启动 B 端管理后台（admin）

### 5.1 安装依赖

```bash
cd frontend/admin
npm install
```

### 5.2 启动开发服务器

```bash
npm run dev
```

默认访问地址：<http://localhost:5175>

> Vite 配置中已将 `/api` 代理到 `http://127.0.0.1:8000`，确保后端已启动。

### 5.3 登录后台

1. 打开 <http://localhost:5175/login>
2. 输入你在第 3 步创建的账号，例如：
   - 用户名：`admin`
   - 密码：`123123`
3. 登录成功后会跳转到 `/batches`：
   - `GET /api/admin/batches/` 返回批次列表（需要 JWT）。
   - 可新建、编辑批次，或一键克隆批次（`/api/admin/batch/clone`）。

---

## 6. 启动 C 端 H5 溯源页面（h5）

### 6.1 安装依赖

```bash
cd frontend/h5
npm install
```

### 6.2 启动开发服务器

```bash
npm run dev
```

默认访问地址：<http://localhost:5173>

### 6.3 测试溯源页面

假设已通过 `init_batch.py` 插入了 `batch_id = TEST-20250101` 的示例批次：

- 通过 query 访问：

  ```text
  http://localhost:5173/trace?batch_id=TEST-20250101
  ```

- 或通过路径访问：

  ```text
  http://localhost:5173/trace/TEST-20250101
  ```

H5 页面会调用：

```http
GET /api/trace/TEST-20250101
```

- 后端自动将该批次的 `scan_count` +1，并记录一条 `ScanLog`。
- 返回当前批次溯源信息和 `scan_count`，页面顶部根据次数显示软防伪提示：
  - `< 5` 次：绿色盾牌“正品校验通过，第 N 次查询”。
  - `>= 5` 次：红色警示“该码已被查询 N 次，谨防假冒”。

---

## 7. 核心接口说明（简要）

### 7.1 C 端溯源接口

- `GET /api/trace/{batch_id}`
  - 自动 `scan_count + 1`。
  - 记录一条 `ScanLog`（批次、IP、时间）。
  - 返回该批次的核心字段：
    - `product_name`
    - `origin_info` / `process_info` / `logistics_static` / `quality_report`（JSON 字符串）
    - `scan_count`
    - `status`

### 7.2 管理端登录

- `POST /api/auth/token`
  - OAuth2 password 模式，表单字段：`username`, `password`。
  - 返回：`{"access_token": "...", "token_type": "bearer"}`。

前端 admin 会将 token 写入 `localStorage.admin_token`，并在所有 `/api/admin/*` 请求头中附带：

```http
Authorization: Bearer <token>
```

### 7.3 批次管理接口（需 JWT）

- `GET /api/admin/batches/`：列表 + 简单筛选。
- `GET /api/admin/batches/{batch_id}/`：获取单条。
- `POST /api/admin/batches/`：创建批次。
- `PUT /api/admin/batches/{batch_id}/`：更新批次。
- `DELETE /api/admin/batches/{batch_id}/`：删除批次。
- `POST /api/admin/batch/clone`：克隆批次（入参：`old_batch_id`, `new_batch_id?`）。

---

## 8. 注意事项

- 当前使用 SQLite 作为存储，`backend/models.py` 中的 `SQLALCHEMY_DATABASE_URL` 可更换为 MySQL 连接串进行迁移。
- 所有 JSON 字段在 DB 中以 `Text` 存储，前端负责 `JSON.parse`，后续可根据需要改为真正的 JSON 类型（例如 MySQL 的 `JSON`）。
- 本项目为 MVP 版本，仅实现基础防伪逻辑与溯源展示，正式环境需要增加：
  - 更完善的权限体系与日志审计。
  - 输入校验与 JSON 结构校验。
  - 更完备的错误处理和安全策略。
