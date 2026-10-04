// Mirrors api/app/schemas.py DocumentRead.
export interface DocumentResult {
  id: number | null
  created_at: string | null
  document_type: string
  issuer: string | null
  deadline: string | null
  amount_due: number | null
  required_actions: string[]
  is_suspicious: boolean
  fraud_reason: string | null
  confidence: 'high' | 'medium' | 'low'
  explanation: string
}

// Mirrors api/app/schemas.py VoiceAnswerRead.
export interface VoiceAnswer {
  question: string
  answer: string
  confidence: 'high' | 'medium' | 'low'
  document_id: number | null
}
