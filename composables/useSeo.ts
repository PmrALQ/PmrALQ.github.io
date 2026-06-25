export function useSeo() {
  const { t, locale } = useI18n()
  const route = useRoute()

  const title = computed(() => {
    const routeTitle = route.meta?.title as string | undefined
    const siteName = t('siteName')
    return routeTitle ? `${routeTitle} — ${siteName}` : siteName
  })

  const description = computed(() => {
    const routeDescription = route.meta?.description as string | undefined
    return routeDescription || t('home.hero.description')
  })

  const localeOg = computed(() =>
    locale.value === 'zh' ? 'zh_CN' : 'en_US'
  )

  return { title, description, localeOg }
}
