export const prerender = false;

// Simple in-memory rate limiting map
const _subscriptions = new Set<string>();

export async function POST({ request }: { request: Request }) {
  try {
    const data = await request.json();
    const email = (data.email || "").trim().toLowerCase();
    const company = (data.company || "").trim(); // Honeypot field

    // 1. Bot Honeypot Check (bots fill out hidden fields, real users do not)
    if (company) {
      return new Response(JSON.stringify({ ok: true, msg: "Subscribed" }), {
        status: 200,
        headers: { "Content-Type": "application/json" }
      });
    }

    // 2. Email Validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email || !emailRegex.test(email)) {
      return new Response(JSON.stringify({ ok: false, error: "invalid_email" }), {
        status: 400,
        headers: { "Content-Type": "application/json" }
      });
    }

    // 3. Already subscribed check
    if (_subscriptions.has(email)) {
      return new Response(JSON.stringify({ ok: true, already: true }), {
        status: 200,
        headers: { "Content-Type": "application/json" }
      });
    }

    _subscriptions.add(email);

    return new Response(JSON.stringify({ ok: true, already: false }), {
      status: 200,
      headers: { "Content-Type": "application/json" }
    });
  } catch (err) {
    return new Response(JSON.stringify({ ok: false, error: "server_error" }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }
}
