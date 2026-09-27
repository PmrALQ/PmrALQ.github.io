/**
 * Splash state — coordinates the CloudSplash intro with the hero entrance
 * on the home page.
 *
 * Using `useState` instead of a module-level `ref`:
 * - SSR: each request gets an isolated state, so a value set during one
 *   request can never leak into another user's response.
 * - Client: the flag is shared across client-side navigation, which is
 *   exactly what the splash / hero hand-off needs.
 */

export function useSplash() {
  const splashFinished = useState<boolean>('splash-finished', () => false)

  function markSplashFinished() {
    splashFinished.value = true
  }

  return { splashFinished, markSplashFinished }
}
