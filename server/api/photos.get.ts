import { readdirSync, statSync } from 'fs'
import { join, extname } from 'path'

const IMAGE_EXTS = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif']

export default defineEventHandler(() => {
  const galleryDir = join(process.cwd(), 'public', 'images', 'gallery')
  const photos: Array<{ src: string; title: string; date: string }> = []

  try {
    const files = readdirSync(galleryDir)
    for (const file of files) {
      const ext = extname(file).toLowerCase()
      if (!IMAGE_EXTS.includes(ext)) continue

      const filePath = join(galleryDir, file)
      const stat = statSync(filePath)

      photos.push({
        src: `/images/gallery/${file}`,
        title: file.replace(ext, '').replace(/[-_]/g, ' '),
        date: stat.mtime.toISOString().split('T')[0],
      })
    }
    // Sort newest first
    photos.sort((a, b) => b.date.localeCompare(a.date))
  } catch {
    // Directory doesn't exist or is empty — return empty array
  }

  return photos
})
