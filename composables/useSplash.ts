/**
 * Module-level splash state — coordinates the CloudSplash intro with the
 * hero entrance on the home page. `splashFinished` flips to true once the
 * splash has played (or was skipped); the home page watches it to start
 * its hero timeline.
 */

const splashFinished = ref(false)

export function useSplash() {
  function markSplashFinished() {
    splashFinished.value = true
  }

  return { splashFinished, markSplashFinished }
}
