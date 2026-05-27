<%def name="make_pagination(total, current)">
    <div class="pagination">
        % if current > 1:
        <a href="page_list_${current-1}.html">&lt;&lt;</a>
        % endif
        % for i in range(1,6):
        <a href="page_list_${i}.html" ${'class="current-page"' if current == i else ''}>${i}</a>
        % endfor
        % if current < total:
        <a href="page_list_${current+1}.html">&gt;&gt;</a>
        % endif
    </div>
</%def>

<div id="mainbar">
    <h1>${title}</h1>
    % for post in posts:
    <div class="post-card">
        <a href="${config.website_address}${post.link}"><h2>${post.title}</h2></a>
        <a class="link-style2" href="${post.category.link}">${post.category.name}</a>
        <div>${post.intro}</div>
        <blockquote>
            <p>
                Post on ${post.date.strftime("%Y-%m-%d")} |
                views: <span class="page-view" link="${post.link}">loading...</span> |
                comment: <span class="comment-count" link="${post.link}">loading...</span>
            </p>
        </blockquote>
    </div>
    % endfor
    ${make_pagination(total_pages, current_page)}
</div>

${sidebar}
