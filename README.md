# wilton

<div align="center">

![wilton.png](./docs/wilton.png)

</div>

为撰写技术博客设计的终端风格的静态站点生成器

访问量统计和评论区服务目前用的是腾讯的 EdgeOne, 之后会加入更多平台的支持

## 使用方法

### pip 安装

```sh
pip install wilton
wilton --src="你的博客源码目录" --dist="输出目录"
```

### uv 安装

```sh
uv tool install wilton
uvx wilton --src="你的博客源码目录" --dist="输出目录"
```

## 部分外观展示

### 主页

![img1](./docs/img1.png)

### 文章阅读页面

![img2](./docs/img2.png)

目前 wilton 支持所有 CommonMark 语法

额外支持:

* 表格
* github alert 消息
* latex 公式
* 高亮文本
* 脚注

### 搜索页

![img3](./docs/img3.png)

## 构建流程

目前的构建流程是这样的:

1. 初始化数据库与模型
2. 解析用户输入
3. 读取配置文件
4. 导入依赖配置但与博客内容无关的资产
    1. css/js/fonts 主题文件和 attachments 目录
    2. 图标
    3. 云函数
5. 扫描博客文件夹 一边扫描一边构建数据库
6. 编译文章与页面
7. 根据数据库生成构建产物
    1. 生成导航栏
    2. 生成侧边栏
    3. 生成文章
    4. 生成页面
        1. 自定义页面
        2. 友情链接页面
        3. 搜索页
    5. 生成文章列表
    6. 网站地图
8. 编译静态索引

## TODO

计划加入的功能 (顺序不代表优先级):

- [ ] 构建缓存与增量编译
- [ ] 切换颜色主题; 毕竟是终端风格, **理论上**用一个类似 Color Scheme 的机制就能实现这一点
- [ ] 支持更多部署平台
  - [ ] cloudflare pages
  - [ ] vercel
  - [ ] 个人服务器, 基于 nginx + fastapi
- [ ] 支持 mermaid 图表
- [ ] 完善的使用文档与二次开发文档
- [ ] 并行化构建, 加快构建速度
- [ ] i18n

如有其他您期望的功能, 可以在 issue 中留言
