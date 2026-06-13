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
