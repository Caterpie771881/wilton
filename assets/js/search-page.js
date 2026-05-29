(async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const keyword = urlParams.get("q");

    if (!keyword) {
        document.getElementById("results").innerHTML =
            '<div class="no-results">请输入搜索关键词</div>';
        return;
    }

    document.getElementById("results").innerHTML =
        '<div class="loading">搜索中...</div>';

    const { init, search } = await import("/pagefind/pagefind.js");
    await init();

    const searchResult = await search(keyword);

    if (!searchResult || searchResult.results.length === 0) {
        document.getElementById("results").innerHTML =
            `<div class="no-results">未找到与 "${keyword}" 相关的内容</div>`;
        return;
    }

    const resultsHtml = [];
    for (const result of searchResult.results.slice(0, 20)) {
        const data = await result.data();
        resultsHtml.push(`
            <div class="post-card">
                <a href="${data.url}"><h2>${data.meta?.title || "无标题"}</h2></a>
                <div class="wrap">${data.excerpt || ""}</div>
                <blockquote>
                    <p>${data.meta?.date ? `Post on ${data.meta.date}` : ""}</p>
                </blockquote>
            </div>
            `);
    }

    document.getElementById("results").innerHTML =
        `<p>找到 ${searchResult.results.length} 条结果</p>${resultsHtml.join("")}`;
})();
