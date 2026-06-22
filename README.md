# 冶金跳蚤市场 - 二手物品交易平台

基于 Django 6.0 的二手物品交易平台，数据库使用 **MySQL**。

## 功能

- 用户注册、登录、个人资料管理
- 商品发布（标题、描述、价格、成色、分类、多图上传）
- 商品浏览、搜索、分类筛选、价格筛选
- 商品详情页、相关推荐
- 收藏/取消收藏
- 站内消息联系卖家
- 个人面板管理（发布的商品、收藏、消息）

## 快速启动

### 方式一：Docker Compose（推荐，自动包含 MySQL）

```bash
docker compose up --build
```

首次启动后，进入容器创建管理员账号：

```bash
docker compose exec web python3 manage.py createsuperuser
```

访问 http://localhost:8000

### 方式二：本地手动启动

1. 安装并启动 MySQL，创建数据库和账号：

```sql
CREATE DATABASE class_project CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'class_project'@'localhost' IDENTIFIED BY 'class_project';
GRANT ALL PRIVILEGES ON class_project.* TO 'class_project'@'localhost';
FLUSH PRIVILEGES;
```

2. 复制环境变量文件并按需修改：

```bash
cp .env.example .env
```

3. 安装依赖（Ubuntu/Debian 需先装 MySQL 头文件用于编译 mysqlclient）：

```bash
apt-get install -y default-libmysqlclient-dev pkg-config build-essential
pip install -r requirements.txt
```

4. 执行迁移并启动：

```bash
python3 manage.py migrate
python3 manage.py createsuperuser
python3 manage.py runserver 0.0.0.0:8000
```

访问 http://localhost:8000

## 数据库配置

数据库连接信息通过环境变量读取（见 `.env.example`），默认值：

| 变量 | 默认值 | 说明 |
|---|---|---|
| DB_NAME | class_project | 数据库名 |
| DB_USER | class_project | 用户名 |
| DB_PASSWORD | class_project | 密码 |
| DB_HOST | 127.0.0.1 | 主机地址（Docker 中为 `db`） |
| DB_PORT | 3306 | 端口 |

## 管理员

```
用户名: admin
密码:   admin123
```

> 注：原 SQLite 中的账号密码等数据不会自动迁移，请在新数据库上通过 `createsuperuser` 重新创建管理员，或参考下方"数据迁移"自行导出导入旧数据。

管理员后台: http://localhost:8000/admin/

## 初始分类

电子产品、服装鞋包、家居生活、图书文具、运动户外、美妆个护、母婴用品、乐器、其他

## 项目结构

```
├── config/         # Django 项目配置
├── accounts/       # 用户认证 app
├── items/          # 商品管理 app
├── core/           # 核心功能 app
├── templates/      # 页面模板
├── static/         # 静态文件
├── media/          # 上传文件
├── deploy/         # 部署脚本与 nginx 配置
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── manage.py       # Django 管理脚本
```

## 从旧版 SQLite 迁移数据（可选）

如果你有旧的 `db.sqlite3` 且想保留其中的数据，可以用 Django 自带的 dumpdata / loaddata：

```bash
# 在旧的 SQLite 环境下导出（需临时把 settings.py 改回 sqlite3 引擎执行这一步）
python3 manage.py dumpdata --natural-foreign --natural-primary \
    -e contenttypes -e auth.Permission \
    --indent 2 > data_backup.json

# 切回 MySQL 配置后导入
python3 manage.py migrate
python3 manage.py loaddata data_backup.json
```

