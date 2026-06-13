import { formatNumber, md5 } from "../../lib/utils";

export async function onRequest({ request }) {
    if (request.method !== "POST") {
        return new Response("Method Not Allowed", { status: 405 });
    }

    try {
        const body = await request.json();
        /** @type {string} */
        const page = body.page;

        if (!page) {
            return new Response("Required: page", { status: 400 });
        }

        const key = md5(page);
        let count = (await view_counter.get(key)) ?? "0";
        count = Number(count) + 1;

        await view_counter.put(key, String(count));

        return new Response(
            JSON.stringify({
                page: page,
                pv: count,
                pv_abbr: formatNumber(count),
            }),
            {
                headers: { "Content-Type": "application/json" },
            },
        );
    } catch (error) {
        return new Response(JSON.stringify({ error: error.message }), {
            status: 500,
            headers: { "Content-Type": "application/json" },
        });
    }
}
