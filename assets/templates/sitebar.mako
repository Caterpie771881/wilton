<%def name="make_search_box()">
    <div>
        搜索: <input class="search" type="text" />
        <button class="button-style1">Go!</button>
    </div>
</%def>

<%def name="make_recent_posts(posts)">
    <div>
        <h2>最近文章</h2>
        <ul>
            % for post in posts:
            <li>${post.title}</li>
            <div class="post-date">${post.post_date}</div>
            % endfor
        </ul>
    </div>
</%def>

<%def name="make_cateory_list(categories)">
    <div>
        <h2>文章类别</h2>
        <ul>
            % for cateory in categories:
            <li>${cateory.name} <span class="cateory-num">${cateory.count}</span></li>
            % endfor
        </ul>
    <div>
</%def>

<%def name="make_link_cloud(links)">
    <div>
        <h2>标签云</h2>
        <div class="link-cloud">
            % for link in links:
            <a href="${link.href}" class="link-style1">${link.name}</a>
            % endfor
        </div>
    </div>
</%def>
