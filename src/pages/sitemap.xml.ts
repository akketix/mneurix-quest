import { getCollection } from 'astro:content';
import { SITE_CONFIG } from '../config';

export async function GET() {
  const posts = await getCollection('news');
  const sortedPosts = posts.sort((a, b) => new Date(b.data.date).getTime() - new Date(a.data.date).getTime());

  const baseUrl = SITE_CONFIG.url;

  const staticPages = [
    { url: '/', priority: '1.0', changefreq: 'daily' },
    { url: '/genre/rts', priority: '0.9', changefreq: 'daily' },
    { url: '/genre/mmo', priority: '0.9', changefreq: 'daily' },
    { url: '/genre/rpg', priority: '0.9', changefreq: 'daily' },
    { url: '/genre/hardware', priority: '0.9', changefreq: 'daily' },
    { url: '/tools/specs-calculator', priority: '0.8', changefreq: 'weekly' },
    { url: '/about', priority: '0.7', changefreq: 'monthly' },
    { url: '/cookies', priority: '0.5', changefreq: 'monthly' },
    { url: '/privacy', priority: '0.5', changefreq: 'monthly' },
    { url: '/terms', priority: '0.5', changefreq: 'monthly' },
    { url: '/licensing', priority: '0.5', changefreq: 'monthly' },
  ];

  const articlesXml = sortedPosts.map(post => {
    const pubDate = new Date(post.data.date).toISOString().split('T')[0];
    return `
    <url>
      <loc>${baseUrl}/news/${post.slug}</loc>
      <lastmod>${pubDate}</lastmod>
      <changefreq>weekly</changefreq>
      <priority>0.8</priority>
    </url>`;
  }).join('');

  const staticXml = staticPages.map(page => `
    <url>
      <loc>${baseUrl}${page.url}</loc>
      <lastmod>${new Date().toISOString().split('T')[0]}</lastmod>
      <changefreq>${page.changefreq}</changefreq>
      <priority>${page.priority}</priority>
    </url>`).join('');

  const sitemapXml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${staticXml}
${articlesXml}
</urlset>`;

  return new Response(sitemapXml.trim(), {
    headers: {
      'Content-Type': 'application/xml',
      'Cache-Control': 'public, max-age=3600'
    }
  });
}
