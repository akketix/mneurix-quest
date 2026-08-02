import { defineCollection, z } from 'astro:content';

const newsCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    date: z.string().or(z.date()),
    gameTitle: z.string(),
    developer: z.string(),
    genre: z.enum(['RTS', 'MMO', 'RPG', 'HARDWARE']),
    platforms: z.array(z.string()),
    releaseWindow: z.string(),
    heroImage: z.string(),
    trailerId: z.string().optional(),
    impactScore: z.number().min(1).max(10).default(8),
    sourceUrl: z.string().url().optional(),
    summary: z.string(),
    specs: z.object({
      minimum: z.string().optional(),
      recommended: z.string().optional()
    }).optional()
  })
});

export const collections = {
  news: newsCollection
};
