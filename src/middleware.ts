import { defineMiddleware } from 'astro:middleware';

// Applies security response headers to on-demand (SSR) responses
// (e.g. /api/status, /api/waitlist). Prerendered HTML pages get equivalent
// coverage via <meta> tags in Layout.astro (referrer + frame-ancestors CSP).
export const onRequest = defineMiddleware(async (_context, next) => {
  const response = await next();
  try {
    response.headers.set('X-Content-Type-Options', 'nosniff');
    response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
    response.headers.set('X-Frame-Options', 'SAMEORIGIN');
    response.headers.set(
      'Permissions-Policy',
      'camera=(), microphone=(), geolocation=(), browsing-topics=(), interest-cohort=()'
    );
  } catch {
    // Headers immutable (body already streamed) — skip silently.
  }
  return response;
});