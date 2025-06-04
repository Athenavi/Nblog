# Nblog - 一个现代化的 Django 博客系统

![Django Version](https://img.shields.io/badge/django-5.2.1+-green)
![Python Version](https://img.shields.io/badge/python-3.13+-blue)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

Nblog 是一个基于 Django 框架开发的全功能博客系统，旨在为开发者提供一个简洁、高效且易于扩展的博客开发起点。项目采用现代 Web 开发实践，包含用户认证、文章管理、分类标签系统等核心功能，并使用 Tailwind CSS 实现响应式设计。

[![GitHub stars](https://img.shields.io/github/stars/Athenavi/Nblog?style=social)](https://github.com/Athenavi/Nblog)
[![GitHub forks](https://img.shields.io/github/forks/Athenavi/Nblog?style=social)](https://github.com/Athenavi/Nblog/fork)

## ✨ 功能特性

### 核心功能
- **文章管理系统**
  - 富文本编辑器支持（开发中）
  - 文章草稿和发布状态管理
  - 按发布时间和更新时间排序
- **媒体管理系统**
  - 多选项分类管理
  - 双视图管理（卡片视图/表格视图）
  - 按名称/类别过滤
- **用户认证系统**
  - 基于 Django Auth 的用户注册/登录
  - 用户权限管理
  - 密码重置功能
- **评论系统**（基础版，待扩展）
  - 文章评论功能
  - 评论审核机制

### 高级功能
- **响应式设计**
  - 使用 Tailwind CSS 实现
  - 适配移动设备和桌面端
- **后台管理**
  - Django Admin (simpleui)
  - 数据可视化仪表盘
  - 批量操作支持

### 扩展功能（规划中）
- 🔜 全文搜索
- 🔜 社交媒体分享
- 🔜 多语言支持

## 📁 项目结构

```
Nblog/
├── core/                   # 核心应用
│   ├── migrations/         # 数据库迁移文件
│   ├── templates/          # 应用专用模板
│   │   └── core/           # 核心模板目录
│   ├── static/             # 应用静态资源
│   │   └── core/           # CSS/JS/图片资源
│   ├── models.py           # 数据模型定义
│   ├── views.py            # 视图逻辑
│   ├── urls.py             # 应用路由配置
│   ├── admin.py            # 后台管理配置
│   ├── forms.py            # 表单定义
│   ├── apps.py             # 应用配置
│   └── tests.py            # 单元测试
│
├── Nblog/                  # 项目配置
│   ├── settings/           # 设置文件（拆分环境）
│   │   ├── base.py         # 基础配置
│   │   ├── development.py  # 开发环境配置
│   │   └── production.py   # 生产环境配置
│   ├── urls.py             # 主路由配置
│   └── wsgi.py             # WSGI 入口
│
├── static/                 # 全局静态资源
│   ├── css/                # 编译后的CSS
│   ├── js/                 # 全局JavaScript
│   └── images/             # 全局图片资源
│
├── templates/              # 全局模板
│   ├── base.html           # 基础模板
│   ├── includes/           # 模板片段
│   └── registration/       # 认证相关模板
│
├── .gitignore              # Git忽略规则
├── manage.py               # Django管理脚本
├── requirements.txt        # 依赖列表
├── README.md               # 项目文档
└── tailwind.config.js      # Tailwind配置
```

## 🚀 快速开始

### 前置条件
- Python 3.13+

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/Athenavi/Nblog.git
   cd Nblog
   ```

2. **创建并激活虚拟环境**
   ```bash
   python -m venv venv
   # Linux/macOS
   source venv/bin/activate
   # Windows
   venv\Scripts\activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**
   ```bash
    cp .env.example .env  # 创建副本
    nano .env             # 编辑环境变量
   ```

5. **配置环境变量**
   复制示例环境文件并配置：
   ```bash
   cp .env.example .env
   ```
   编辑 `.env` 文件设置你的环境变量

6. **应用数据库迁移**
   ```bash
   python manage.py migrate
   ```

7. **创建管理员账户**
   ```bash
   python manage.py createsuperuser
   ```

8. **启动开发服务器**
   ```bash
   python manage.py runserver
   ```

现在访问以下地址：
- 博客首页：http://127.0.0.1:8000/
- 管理后台：http://127.0.0.1:8000/admin/

## 🧪 测试
运行测试套件：

```bash
python manage.py test core
```

## 🌐 部署到生产环境（可选）#未经测试

### Docker 部署方式
使用 Docker + Gunicorn + Nginx

1. 构建 Docker 镜像：
   ```bash
   docker build -t nblog .
   ```

2. 运行容器：
   ```bash
   docker run -d -p 8000:8000 --env-file .env --name nblog_instance nblog
   ```

3. 配置 Nginx 反向代理（示例配置见 `deployment/nginx.conf`）

### 其他部署选项
- Heroku
- PythonAnywhere
- AWS Elastic Beanstalk

**Happy Blogging!** 🎉 使用 Nblog 轻松构建您的个人博客空间。