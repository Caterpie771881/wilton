<%inherit file="base.mako"/>

<%block name="title">${post.title}</%block>

<%block name="main">
<% website_address = ctx.config.website_address %>
<div id="mainbar">
    <div class="post-meta">
        <div class="post-title" data-pagefind-meta="title">${post.title}</div>
        <div>
            ${(
                f'<a class="link-style2" href="{website_address}{post.category.link}">{post.category.name}</a>'
                + ''.join([
                    f'&nbsp;<a class="tag" href="{website_address}{tag.link}">{tag.name}</a>'
                    for tag in post.tags
                ])
            )}
        </div>
        <blockquote>
            <p>
                Post on <span data-pagefind-meta="date">${post.date.strftime("%Y-%m-%d")}</span>
                |
                views: <span class="page-view">loading...</span>
                |
                comment: <span class="comment-count">loading...</span>
            </p>
        </blockquote>
    </div>
    <div class="post-content" data-pagefind-body>
        ${post.content}
    </div>
    <hr class="end-of-file"/>
    <div class="comment-area">
        <h2>评论区</h2>
        <form class="comment-form" id="comment-form">
            <h3>发表评论</h3>
            <div class="form-line">
                <div>
                    昵称 <input class="input-style1" name="name" type="text" placeholder="必填"/>
                </div>
                <div>
                    邮箱 <input class="input-style1" name="email" type="text" placeholder="选填"/>
                </div>
                <div>
                    网址 <input class="input-style1" name="link" type="text" placeholder="选填"/>
                </div>
            </div>
            <textarea name="content" placeholder="在这里输入您的留言..."></textarea>
            <div style="margin: 0; text-align: center">
                <button class="link-style2">发送评论</button>
            </div>
        </form>
        <h3>所有评论</h3>
        <div class="comment-list" id="comment-list">暂无评论...</div>
    </div>
</div>
${sidebar}
</%block>

<%block name="script">
<% website_address = ctx.config.website_address %>
<script src="${website_address}/js/comment-area.js"></script>
<script>
addViewCount("${website_address}", "${post.link}");
loadCommentArea("${website_address}", "${post.link}");
bindSubmitCommentEvent("${website_address}", "${post.link}");
</script>
</%block>
