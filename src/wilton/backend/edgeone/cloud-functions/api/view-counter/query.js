import { formatNumber, md5 } from "../../lib/utils";

export async function onRequest({ request }) {
    if (request.method !== "POST") {
        return new Response("Method Not Allowed", { status: 405 });
    }

    try {
        const body = await request.json();
        /** @type {string[]} */
        const pages = body.pages ?? [];

        const results = await Promise.all(
            pages.map(async (page) => {
                const key = md5(page);
                /** @type {string} */
                const count = (await view_counter.get(key)) ?? "0";
                return { page, value: formatNumber(Number(count)) };
            }),
        );

        const result = {};
        for (const { page, value } of results) {
            result[page] = value;
        }

        return new Response(JSON.stringify(result), {
            headers: { "Content-Type": "application/json" },
        });
    } catch (error) {
        return new Response(JSON.stringify({ error: error.message }), {
            status: 500,
            headers: { "Content-Type": "application/json" },
        });
    }
}
