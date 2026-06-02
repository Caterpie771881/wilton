<!doctype html>
<html>
    <head>
        <meta charset="utf-8" />
        <title>搜索结果</title>
        <link rel="stylesheet" href="${website_address}/css/wilton.css" />
        <script src="${website_address}/js/wilton.js"></script>
    </head>
    <body>
        <div id="container">
            ${navbar}
            <div id="main">
                <div id="mainbar">
                    <h1>搜索结果</h1>
                    <div id="results"><div>正在导入资源...</div></div>
                </div>
                <div id="sidebar">
                    ${sidebar}
                </div>
            </div>
            ${footer}
        </div>
    </body>
</html>

<script type="module">
    import { getSearchResults } from "${website_address}/js/search-page.js";

    const urlParams = new URLSearchParams(window.location.search);
    const keyword = urlParams.get("q");

    getSearchResults(keyword);
</script>
