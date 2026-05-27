<div id="mainbar">
    <div class="post-meta">
        <div class="post-title">${post.title}</div>
        <div>
            <a class="link-style2" href="${config.website_address}${post.category.link}">${post.category.name}</a>
            % for tag in post.tags:
            <a class="tag" href="${config.website_address}${tag.link}">${tag.name}</a>
            % endfor
        </div>
        <blockquote>
            <p>Post on ${post.date.strftime("%Y-%m-%d")} | views: <span>loading...</span> | comment: <span>loading...</span></p>
        </blockquote>
    </div>
    <div class="post-content">
        ${post.content}
    </div>
</div>
<div id="sidebar">
    <div>
        搜索: <input class="search" type="text" />
        <button class="button-style1">Go!</button>
    </div>
    <div class="catalogue">
        <h2>文章目录</h2>
    </div>
</div>
