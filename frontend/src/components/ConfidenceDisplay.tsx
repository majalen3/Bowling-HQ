interface Props {
  score: number
  size?: 'sm' | 'md' | 'lg'
}

function color(score: number) {
  if (score >= 85) return 'text-green-400'
  if (score >= 70) return 'text-yellow-400'
  return 'text-orange-400'
}

function label(score: number) {
  if (score >= 90) return 'Excellent'
  if (score >= 80) return 'Strong'
  if (score >= 70) return 'Good'
  if (score >= 60) return 'Acceptable'
  return 'Low'
}

export default function ConfidenceDisplay({ score, size = 'md' }: Props) {
  const textSize = size === 'lg' ? 'text-4xl' : size === 'md' ? 'text-2xl' : 'text-lg'

  return (
    <div className="flex items-baseline gap-2">
      <span className={`${textSize} font-bold ${color(score)}`}>{score.toFixed(0)}%</span>
      <span className="text-sm text-gray-400">{label(score)}</span>
      <div className="flex-1 bg-gray-700 rounded-full h-2 ml-1">
        <div
          className={`h-2 rounded-full transition-all ${color(score).replace('text-', 'bg-')}`}
          style={{ width: `${score}%` }}
        />
      </div>
    </div>
  )
}
