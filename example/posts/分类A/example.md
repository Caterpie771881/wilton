+++
title = "示例文章"
post_date = 2026-01-01
tags = [ "示例" ]
+++
这是一篇示例文章, 展示了 wilton 的 markdown 编译器支持的语法

# H1 标题
## H2 标题
### H3 标题
#### H4 标题
##### H5 标题

---

# 文本样式

普通文本 hello world

**加粗文本 hello world**

*斜体文本 hello world*

~~删除线文本 hello world~~

<u>下划线文本 hello world</u>

==高亮文本 hello world==

`行内代码 hello world`

---

# 链接

[普通链接](https://www.example.com)

[带标题的链接](https://www.example.com "示例网站")

直接链接: <https://www.example.com>

[相对路径链接](/about)

[引用链接][id]

[id]: https://www.example.com/reference "参考链接"

---

# 图片

你可以引用外部的图片

![img1](https://disk.sample.cat/samples/png/monalisa-200x200.png)

你也可以引用本地图片, wilton 会将其引用地址替换为你的网站地址

![img2](example.png)

---

# 列表

## 无序列表

- 项目 1
- 项目 2
  - 嵌套项目 2.1
  - 嵌套项目 2.2
- 项目 3

## 有序列表

1. 第一项
2. 第二项
   1. 嵌套第二项 2.1
   2. 嵌套第二项 2.2
3. 第三项

## 任务列表

- [x] 已完成任务
- [ ] 未完成任务
- [ ] 待办事项 1
  - [x] 子任务 1.1
  - [ ] 子任务 1.2
- [ ] 代办事项 2

---

# 表格

| 表头 1 | 表头 2 | 表头 3 |
| ------ | ------ | ------ |
| 单元格 1 | 单元格 2 | 单元格 3 |
| 单元格 4 | 单元格 5 | 单元格 6 |

---

# 代码块

wilton 使用 `hightlight.js` 支持多种代码格式的自动识别与高亮

## python 代码示例

```python
def fibonacci(n: int) -> list[int]:
    """生成斐波那契数列前n项"""
    a, b = 0, 1
    return [a := b, b := a + b][:n]  # 使用海象运算符实现

if __name__ == "__main__":
    nums = fibonacci(10)
    print(f"前10项斐波那契数列: {', '.join(map(str, nums))}")
```

## javascript 代码示例

```javascript
const fetchUser = async (id) => {
  return new Promise((resolve) => {
    setTimeout(() => resolve({ id, name: `User${id}` }), 100);
  });
};

const displayUsers = async () => {
  const ids = [1, 2, 3];
  const users = await Promise.all(ids.map(fetchUser));
  users.forEach(({ name }) => console.log(`Hello, ${name}!`));
};

displayUsers();
```

## golang 代码示例

```go
package main

import "fmt"

type Greeter struct {
	Greeting string
}

func (g Greeter) Greet(name string) string {
	return fmt.Sprintf("%v, %v!", g.Greeting, name)
}

func main() {
	g := Greeter{Greeting: "你好"}
	fmt.Println(g.Greet("世界"))
}
```

---

# Latex 公式

wilton 使用 `katex.js` 进行公式的渲染

行内公式: $\mathcal{D}_{\gamma,\eta,\rho,n}(p_i)=\left\{T\prod_{i=1}^{n}{p_i}+\text{CRT}_{(p_i)}(r_i)\mid T\in\mathbb{Z}\cap\left[2^{\gamma-1}/\prod_{i=1}^{n}{p_i},2^{\gamma}/\prod_{i=1}^{n}{p_i}\right),r_i\sim\chi_{\rho}\right\}$

公式块

$$
\pmb{J}(\lambda,k)^n=
\left[
\begin{matrix}
\lambda^n&n\lambda^{n-1}&\frac{n(n-1)}{2}\lambda^{n-2}&\cdots&\left(\begin{matrix}n\\k-2\end{matrix}\right)\lambda^{n-k+2}&\left(\begin{matrix}n\\k-1\end{matrix}\right)\lambda^{n-k+1}\\
0&\lambda^n&n\lambda^{n-1}&\cdots&\left(\begin{matrix}n\\k-3\end{matrix}\right)\lambda^{n-k+3}&\left(\begin{matrix}n\\k-2\end{matrix}\right)\lambda^{n-k+2}\\
0&0&\lambda^{n}&\cdots&\left(\begin{matrix}n\\k-4\end{matrix}\right)\lambda^{n-k+4}&\left(\begin{matrix}n\\k-3\end{matrix}\right)\lambda^{n-k+3}\\
\vdots&\vdots&\vdots&&\vdots&\vdots\\
0&0&0&\cdots&\lambda^{n}&n\lambda^{n-1}\\
0&0&0&\cdots&0&\lambda^{n}
\end{matrix}
\right]
$$

---

# GFM Alert 消息

> [!CAUTION]
> 这是一条 CAUTION 级别的消息

> [!WARNING]
> 这是一条 WARNING 级别的消息

> [!TIP]
> 这是一条 TIP 级别的消息

> [!NOTE]
> 这是一条 NOTE 级别的消息

> [!IMPORTANT]
> 这是一条 IMPORTANT 级别的消息
