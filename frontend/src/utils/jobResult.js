/** Confidence score persisted in jobs.json under result.score */
export function getJobConfidence(result) {
  if (!result) return 0
  const value = result.score ?? result.confidence ?? 0
  return typeof value === 'number' ? value : 0
}

export function formatConfidencePercent(result) {
  return Math.round(getJobConfidence(result) * 100)
}
