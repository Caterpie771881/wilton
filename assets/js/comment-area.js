const commentForm = document.getElementById("comment-form");
const commentList = document.getElementById("comment-list");

/**
 * @param {string} nickname
 * @param {string} comment
 * @param {string} date
 * @param {string | undefined} link
 * @param {string | undefined} email
 */
function makeCommentCard(nickname, comment, date, link, email) {
    const commentCard = document.createElement("div");
    commentCard.className = "comment";

    const nicknameElm = document.createElement("strong");
    nicknameElm.innerText = decodeURIComponent(nickname);
    commentCard.appendChild(nicknameElm);

    const content = document.createElement("p");
    content.innerText = decodeURIComponent(comment);
    commentCard.appendChild(content);

    const metaDatasElm = document.createElement("blockquote");
    const metaDatas = [`<span>date: ${escapeHtml(date)}</span>`];
    if (link !== undefined) {
        link = escapeHtml(decodeURIComponent(link));
        metaDatas.push(`<span>link: ${link}</span>`);
    }
    if (email !== undefined) {
        email = escapeHtml(decodeURIComponent(email));
        metaDatas.push(`<span>email: ${email}</span>`);
    }
    metaDatasElm.innerHTML = `<p>${metaDatas.join(" | ")}</p>`;
    commentCard.appendChild(metaDatasElm);

    return commentCard;
}

/**
 * @param {string} websiteAddress
 * @param {string} pageLink
 * @return {Promise<{ date: string; name: string; email: string; link: string; content: string; }[]>}
 */
async function fetchComments(websiteAddress, pageLink) {
    try {
        const resp = await fetch(`${websiteAddress}/api/comments/query`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                pages: [pageLink],
            }),
        });

        if (!resp.ok) {
            throw new Error(`HTTP ${resp.status}: ${resp.statusText}`);
        }

        return (await resp.json())[pageLink] ?? [];
    } catch (error) {
        console.error(`[wilton] 获取评论失败: ${error}`);
        return [];
    }
}

/**
 * @param {string} websiteAddress
 * @param {string} pageLink
 */
async function loadCommentArea(websiteAddress, pageLink) {
    const comments = await fetchComments(websiteAddress, pageLink);

    document.querySelectorAll(".comment-count").forEach((elm) => {
        elm.innerText = comments.length;
    });

    if (commentList === null || comments.length === 0) return;

    try {
        comments.sort((a, b) => b.date.localeCompare(a.date));
        commentList.replaceChildren();
        comments.forEach((data) => {
            const commentCard = makeCommentCard(
                data.name,
                data.content,
                data.date,
                data.link,
                data.email,
            );
            commentList.appendChild(commentCard);
        });
    } catch (error) {
        console.error(`[wilton] 生成历史评论失败: ${error}`);
    }
}

/**
 * @param {string} websiteAddress
 * @param {string} pageLink
 */
function bindSubmitCommentEvent(websiteAddress, pageLink) {
    commentForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const formData = new FormData(commentForm);
        const data = {
            page: pageLink,
            name: formData.get("name"),
            content: formData.get("content"),
        };

        if (formData.get("email")) data.email = formData.get("email");
        if (formData.get("link")) data.link = formData.get("link");

        fetch(`${websiteAddress}/api/comments/add`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        })
            .then((resp) => resp.json())
            .then((data) => {
                commentForm.querySelector("textarea").value = "";
                const commentCard = makeCommentCard(
                    data.name,
                    data.content,
                    data.date,
                    data.link,
                    data.email,
                );
                commentList.prepend(commentCard);
            });
    });
}
