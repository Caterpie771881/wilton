# wilton

为撰写技术博客设计的终端风格的静态站点生成器

## TODO

### 前端

* [ ] 处理 table 元素，给其套上 table-container
* [ ] 面临 table 单元格内的换行时，应如何处理样式
* [x] 文章目录 这个要在生成器直接生成吗
* [ ] 阅读量/评论数/评论内容 的获取
* [ ] 文章内容搜索要怎么做
* [ ] 要支持 GFM 吗

### 后端

能交给前端代工的就交给前端

* [ ] 数据库要存什么
* [ ] 垃圾评论要怎么过滤
* [ ] 阅读量要怎么统计（这个应该是 js 那边的工作）

### 生成器

* [ ] 模板引擎选型 html/template? 是否要将模板编译进可执行程序?
* [ ] TUI 设计

post
|field|type|meta|
|--|--|--|
|id|int|primary|
|title|str||
|category|int|category.id|
|date|str||
|content|str||

category
|field|type|meta|
|--|--|--|
|id|int|primary|
|name|str||

tag
|field|type|meta|
|--|--|--|
|id|int|primary|
|name|str||
