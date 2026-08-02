import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';

export async function GET(context: any) {
  const news = await getCollection('news');
  const sortedNews = news.sort((a, b) => new Date(b.data.date).getTime() - new Date(a.data.date).getTime());

  return rss({
    title: 'MNEURIX // QUEST — Autonomous RTS, MMO & RPG News',
    description: 'High-signal press release breakdowns for Real-Time Strategy, MMO Expansions, and RPG Devlogs.',
    site: context.site || 'https://mneurix.quest',
    items: sortedNews.map((post) => ({
      title: post.data.title,
      pubDate: new Date(post.data.date),
      description: post.data.summary,
      link: `/news/${post.slug}/`,
    })),
    customData: `<language>en-us</language>`,
  });
}
