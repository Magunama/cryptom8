import {Prediction} from "./prediction.model";

export enum PredictionWindow {
  TINY,
  SMALL,
  MEDIUM
}

export enum BaseNNAlgorithm {
  LSTM = 0,
  JORDAN = 1
}

export enum NNAlgorithm {
  LSTM,
  JORDAN,
  LSTM_SEQ,
  JORDAN_SEQ
}

export enum NNModelStatus {
  CREATED,
  IN_TRAINING,
  TRAINED,
  ERRORED
}

export interface NNModel {
  id: number
  algorithm: number
  symbol_name: string
  status: NNModelStatus
  prediction_window: PredictionWindow
  predictions: Prediction[]
  created: Date
  updated: Date
}
