export async function getSearchResults(keyword) {
    const resultsElement = document.getElementById("results");

    if (resultsElement === null) return;

    const no_results = document.createElement("div");
    no_results.className = "no-results";

    if (!keyword) {
        resultsElement.replaceChildren();
        no_results.innerText = "请输入搜索关键词";
        resultsElement.appendChild(no_results);
        return;
    }

    const loading = document.createElement("div");
    loading.className = "loading";
    loading.innerText = "搜索中...";
    resultsElement.replaceChildren();
    resultsElement.appendChild(loading);

    const { init, search } = await import("../pagefind/pagefind.js");
    await init();

    const searchResult = await search(keyword);

    if (!searchResult || searchResult.results.length === 0) {
        resultsElement.replaceChildren();
        no_results.innerText = `未找到与 "${keyword}" 相关的内容`;
        resultsElement.appendChild(no_results);
        return;
    }

    resultsElement.replaceChildren();

    const result_count = document.createElement("p");
    result_count.innerText = `找到 ${searchResult.results.length} 条结果`;
    resultsElement.appendChild(result_count);

    for (const result of searchResult.results.slice(0, 20)) {
        const data = await result.data();

        const post_card = document.createElement("div");
        post_card.className = "post-card";

        const post_title = document.createElement("a");
        post_title.href = data.url;
        post_title.innerHTML = `<h2>${data.meta?.title || "无标题"}</h2>`;
        post_card.appendChild(post_title);

        const excerpt = document.createElement("div");
        excerpt.className = "wrap";
        excerpt.innerHTML = data.excerpt || "";
        post_card.appendChild(excerpt);

        const post_meta = document.createElement("blockquote");
        post_meta.innerHTML = `<p>${data.meta?.date ? `Post on ${data.meta.date}` : ""}</p>`;
        post_card.appendChild(post_meta);

        resultsElement.appendChild(post_card);
    }
}
