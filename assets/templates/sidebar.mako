<%def name="make_search_box()">
    <div class="search-box">
        搜索: <input class="search" type="text" />
        <button class="button-style1">Go!</button>
    </div>
</%def>

<%def name="make_recent_posts(posts)">
    <div>
        <h2>最近文章</h2>
        <ul>
            % for post in posts:
            <li>
                <a
                    style="color: var(--wilton-color-white)"
                    href="${website_address}${post.link}"
                >${post.title}</a>
            </li>
            <div class="post-date">${post.date.strftime("%Y-%m-%d")}</div>
            % endfor
        </ul>
    </div>
</%def>

<%def name="make_cateory_list(categories)">
    <div>
        <h2>文章类别</h2>
        <ul>
            % for cateory in categories:
            <li>
                <a
                    style="color: var(--wilton-color-white)"
                    href="${website_address}${cateory.link}"
                >${cateory.name}</a>
                <span class="cateory-num">${len(cateory.posts)}</span>
            </li>
            % endfor
        </ul>
    </div>
</%def>

<%def name="make_tag_cloud(tags)">
    <div>
        <h2>标签云</h2>
        <div class="link-cloud">
            % for tag in tags:
            <a
                href="${website_address}${tag.link}"
                class="link-style1"
            >${tag.name}</a>
            % endfor
        </div>
    </div>
</%def>

<div id="sidebar">
    ${make_search_box()}
    ${make_recent_posts(posts)}
    ${make_cateory_list(categories)}
    ${make_tag_cloud(tags)}
</div>
