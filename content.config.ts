import { defineContentConfig, defineCollection } from '@nuxt/content'
import { z } from 'zod'

export default defineContentConfig({
  collections: {
    // Blog posts and standalone pages (about, guestbook)
    content: defineCollection({
      type: 'page',
      source: {
        include: '**/*.md',
      },
      schema: z.object({
        title: z.string(),
        description: z.string().optional(),
        date: z.string().optional(),
        tags: z.array(z.string()).optional(),
      }),
    }),

    // Programming projects / games
    // 注意: 真实文件在 content/zh|en/projects/, 需用 **/projects/*.md 才能命中
    projects: defineCollection({
      type: 'page',
      source: {
        include: '**/projects/*.md',
      },
      schema: z.object({
        title: z.string(),
        description: z.string().optional(),
        date: z.string().optional(),
        tags: z.array(z.string()).optional(),
        thumbnail: z.string().optional(),
        demoUrl: z.string().optional(),
        sourceUrl: z.string().optional(),
        tech: z.array(z.string()).optional(),
        type: z.string().optional(),
      }),
    }),

    // Version changelog
    // 注意: 真实文件在 content/zh|en/changelog/, 需用 **/changelog/*.md 才能命中
    changelog: defineCollection({
      type: 'page',
      source: {
        include: '**/changelog/*.md',
      },
      schema: z.object({
        title: z.string(),
        description: z.string().optional(),
        date: z.string(),
        version: z.string(),
      }),
    }),
  },
})
