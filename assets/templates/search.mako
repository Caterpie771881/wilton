<!doctype html>
<html>
    <head>
        <meta charset="utf-8" />
        <title>搜索结果</title>
        <link rel="stylesheet" href="${website_address}/css/wilton.css" />
        <script src="${website_address}/js/wilton.js"></script>
        <script defer type="module" src="${website_address}/js/search-page.js"></script>
    </head>
    <body>
        <div id="container">
            ${navbar}
            <div id="main">
                <div id="mainbar">
                    <h1>搜索结果</h1>
                    <div id="results"></div>
                </div>
                <div id="sidebar">
                    ${sidebar}
                </div>
            </div>
            ${footer}
        </div>
    </body>
</html>
