const textCopy = "copy";
const textCopyied = "copyied✔";

document.addEventListener("DOMContentLoaded", () => {
    try {
        addCodeBlockTips();
        initClipboard();
    } catch (e) {
        console.warn(`[wilton] 代码块样式未启用, 原因: ${e}`);
    }

    try {
        // launch hightlight.js
        hljs.highlightAll();
    } catch (e) {
        console.warn(`[wilton] 代码块语法高亮未启用, 原因: ${e}`);
    }

    try {
        document.querySelectorAll("eq, eqn").forEach((elem) => {
            const latex = elem.textContent;
            // eqn 是块级公式，eq 是行内公式
            const isDisplay = elem.tagName.toLowerCase() === "eqn";

            try {
                katex.render(latex, elem, {
                    displayMode: isDisplay,
                    throwOnError: false,
                    output: "html",
                });
            } catch (error) {
                console.error("KaTeX render error:", error);
                elem.textContent = latex;
            }
        });
    } catch (e) {
        console.warn(`[wilton] Latex 公式渲染未启用, 原因: ${e}`);
    }

    try {
        prepareGallery();
        // launch fancybox.js
        Fancybox.bind("[data-fancybox]", {});
    } catch (e) {
        console.warn(`[wilton] 图片浏览窗口未启用, 原因: ${e}`);
    }

    try {
        let post_content = document.querySelector(".post-content");
        let catalogue = document.querySelector(".catalogue");
        if (post_content && catalogue) {
            catalogue.appendChild(genCatalogue(post_content));
        }
    } catch (e) {
        console.warn(`[wilton] 目录未创建, 原因: ${e}`);
    }

    try {
        let searchBoxes = document.querySelectorAll("div.search-box");
        searchBoxes.forEach((searchBox) => {
            const searchInput = searchBox.querySelector(".input-style1");
            const searchBtn = searchBox.querySelector("button");
            initSearchBox(searchInput, searchBtn);
        });
    } catch (e) {
        console.warn(`[wilton] 初始化搜索栏失败, 原因: ${e}`);
    }
});

/**
 * 处理所有代码块, 添加 markdown 样式的标记和复制按钮
 * @returns {number}
 */
function addCodeBlockTips() {
    // 获取所有未处理的 pre 标签
    const preElements = document.querySelectorAll("pre:not(.hastips)");
    // 只需要 pre > code.language-* 的元素
    const filteredPre = Array.from(preElements).filter((pre) => {
        const code = pre.querySelector("code");
        return code && code.className.includes("language-");
    });
    let i = 0;
    filteredPre.forEach((pre) => {
        // 标记为已处理
        pre.classList.add("hastips");
        // 获取语言类型
        let language = "text";
        code = pre.querySelector("code");
        if (code) {
            const match = code.className.match(/language-(\w+)/);
            language = match ? match[1] : null;
            code.id = `copy${i}`;
        }
        // 代码块上方，需要插入语言类型以及复制框
        const div_befor = document.createElement("div");
        div_befor.className = "code-block-tips";
        div_befor.innerHTML =
            "```" +
            `${language} <button class="button-style2 copy" data-clipboard-target="#copy${i}">${textCopy}</button>`;
        div_befor.style.marginBottom = "0";
        pre.parentNode.insertBefore(div_befor, pre);
        // 代码块下方，插入 ``` 即可
        const div_after = document.createElement("div");
        div_after.className = "code-block-tips";
        div_after.innerText = "```";
        div_after.style.marginTop = "0";
        pre.parentNode.insertBefore(div_after, pre.nextSibling);
        // 更新复制按钮编号
        i++;
    });
    return preElements.length;
}

/**
 * 初始化复制按钮
 */
function initClipboard() {
    let clipboard = new ClipboardJS(".copy");
    clipboard.on("success", (e) => {
        e.clearSelection();
        e.trigger.innerText = textCopyied;
        e.trigger.style.color = "var(--wilton-color-light-green)";
        setTimeout(() => {
            e.trigger.innerText = textCopy;
            e.trigger.style.color = "";
        }, 3000);
    });
    clipboard.on("error", (e) => {
        alert("复制失败，请手动复制");
    });
}

/**
 * 为主栏中的图片添加 fancybox 属性
 */
function prepareGallery() {
    const imgs = document.querySelector("#mainbar").querySelectorAll("img");
    imgs.forEach((img) => {
        img.setAttribute("data-fancybox", "gallery");
    });
}

/**
 * 根据主栏中的 h1/h2/h3 标题生成文章目录
 * @param {HTMLElement} elem
 * @returns {HTMLElement}
 */
function genCatalogue(elem) {
    const headings = elem.querySelectorAll("h1, h2, h3");
    if (headings.length === 0) {
        return document.createElement("ol");
    }
    const catalogue = document.createElement("ol");
    catalogue.className = "catalogue";
    const stack = [{ level: 0, element: catalogue }];

    headings.forEach((heading, index) => {
        const level = parseInt(heading.tagName.substring(1));
        if (!heading.id) {
            heading.id = `heading-${index}`;
        }

        const listItem = document.createElement("li");
        const link = document.createElement("a");
        link.href = `#${heading.id}`;
        link.textContent = heading.textContent || heading.innerText;
        listItem.appendChild(link);

        while (stack.length > 0 && stack[stack.length - 1].level >= level) {
            stack.pop();
        }

        const parent = stack[stack.length - 1].element;

        if (parent.tagName === "OL") {
            parent.appendChild(listItem);
        } else if (parent.tagName === "LI") {
            let nestedOl = parent.querySelector("ol:last-child");
            if (!nestedOl) {
                nestedOl = document.createElement("ol");
                parent.appendChild(nestedOl);
            }
            nestedOl.appendChild(listItem);
        }

        stack.push({
            level: level,
            element: listItem,
        });
    });
    return catalogue;
}

/**
 * 初始化搜索栏
 * @param {HTMLInputElement} searchInput
 * @param {HTMLElement} searchBtn
 */
function initSearchBox(searchInput, searchBtn) {
    // 点击按钮跳转搜索页
    searchBtn.addEventListener("click", () => {
        const keyword = searchInput.value.trim();
        if (keyword) {
            window.location.href = `/search.html?q=${encodeURIComponent(keyword)}`;
        }
    });
    // 回车键激活搜索按钮点击事件
    searchInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            searchBtn.click();
        }
    });
}

/**
 * 获取页面中文章的访问量
 * @param {string} websiteAddress
 */
async function fetchViewCounts(websiteAddress) {
    // 获取页面中所有要获取访问量的链接
    const postCards = document.querySelectorAll("div.post-card");
    /** @type {Object.<string, HTMLElement>} */
    const targets = {};
    /** @type {string[]} */
    const pages = [];
    postCards.forEach((postCard) => {
        const pageViewElm = postCard.querySelector(".page-view");
        if (pageViewElm === null) return;

        const link = pageViewElm.getAttribute("link");
        if (link === null) return;

        pages.push(link);
        targets[link] = pageViewElm;
    });

    // 调用 API 查询访问量
    fetch(`${websiteAddress}/api/view-counter/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            pages: pages,
        }),
    })
        .then((resp) => resp.json())
        .then((data) => {
            for (const link in data) {
                const views = data[link];
                targets[link].innerText = views;
            }
        })
        .catch((error) => {
            console.error(`[wilton] 获取访问量失败, 原因: ${error}`);
        });
}

/**
 * @param {string} websiteAddress
 * @param {string} pageLink
 */
async function addViewCount(websiteAddress, pageLink) {
    const pageViewElms = document.querySelectorAll(".page-view");
    fetch(`${websiteAddress}/api/view-counter/add`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            page: pageLink,
        }),
    })
        .then((resp) => resp.json())
        .then(
            /**
             * @param {{ page: string; pv: number; pv_abbr: string }} data
             */
            (data) => {
                pageViewElms.forEach((elm) => {
                    elm.innerText = data.pv_abbr;
                });
            },
        )
        .catch((error) => {
            console.error(`[wilton] 获取访问量失败, 原因: ${error}`);
        });
}

/**
 * @param {string} text
 * @returns {string}
 */
function escapeHtml(text) {
    return text.replace(/[&<>'"]/g, (m) => {
        switch (m) {
            case "&":
                return "&amp;";
            case "<":
                return "&lt;";
            case ">":
                return "&gt;";
            case "'":
                return "&#39;";
            case '"':
                return "&quot;";
            case " ":
                return "&nbsp;";
        }
    });
}

/**
 * @param {string} websiteAddress
 */
function fetchCommentCounts(websiteAddress) {
    // 获取页面中所有要获取评论数的链接
    const postCards = document.querySelectorAll("div.post-card");
    /** @type {Object.<string, HTMLElement>} */
    const targets = {};
    /** @type {string[]} */
    const pages = [];
    postCards.forEach((postCard) => {
        const commentCountElm = postCard.querySelector(".comment-count");
        if (commentCountElm === null) return;

        const link = commentCountElm.getAttribute("link");
        if (link === null) return;

        pages.push(link);
        targets[link] = commentCountElm;
    });

    // 调用 API 查询评论
    fetch(`${websiteAddress}/api/comments/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            pages: pages,
        }),
    })
        .then((resp) => resp.json())
        .then((data) => {
            for (const link in data) {
                const comments = data[link];
                targets[link].innerText = comments.length;
            }
        })
        .catch((error) => {
            console.error(`[wilton] 获取评论数量失败, 原因: ${error}`);
        });
}
