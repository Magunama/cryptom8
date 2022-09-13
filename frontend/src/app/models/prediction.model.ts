export enum PredictionResult {
  STRONG_BUY,
  BUY,
  HOLD,
  SELL,
  STRONG_SELL
}

export interface Prediction {
  model_id: number,
  result: PredictionResult,
  confidence: number,
  created: Date,
  symbolName: string
}
