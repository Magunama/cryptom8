import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {NNAlgorithm, NNModel, NNModelStatus, PredictionWindow} from "../../../models/nnmodel.model";
import {ModelService} from "../../../services/model.service";
import {take} from "rxjs";
import {Prediction, PredictionResult} from "../../../models/prediction.model";
import {formatDate} from "@angular/common";
import {PredictionService} from "../../../services/prediction.service";
import {MatDialog} from "@angular/material/dialog";
import {ModelDialogStepperComponent} from "../model-dialog-stepper/model-dialog-stepper.component";
import {BarService} from "../../../services/bar.service";

@Component({
  selector: 'app-model-card',
  templateUrl: './model-card.component.html',
  styleUrls: ['./model-card.component.scss']
})
export class ModelCardComponent implements OnInit {

  @Input() dataSource!: string;
  @Input() model!: NNModel;
  @Output() modelDeleted = new EventEmitter<number>();
  @Output() predictionDone = new EventEmitter<Prediction>();
  @Output() trainingStarted = new EventEmitter<number>();

  algorithmEnum: typeof NNAlgorithm = NNAlgorithm;
  statusEnum: typeof NNModelStatus = NNModelStatus;

  constructor(private modelService: ModelService, private predictionService: PredictionService,
              private barService: BarService, private _dialog: MatDialog) {
  }

  ngOnInit(): void {
  }

  trainDisabled(): boolean {
    return this.model.status === NNModelStatus.IN_TRAINING;
  }

  predictDisabled(): boolean {
    return [NNModelStatus.CREATED, NNModelStatus.IN_TRAINING, NNModelStatus.ERRORED].includes(this.model.status);
  }

  deleteModel() {
    // todo: remove datasource & move service call to parent component
    this.modelService.deleteModel(this.dataSource, this.model.id).pipe(take(1)).subscribe();
    this.modelDeleted.emit(this.model.id);
  }

  makePrediction() {
    // todo: remove datasource & move service call to parent component
    this.predictionService.makePrediction(this.dataSource, this.model.id).pipe(take(1)).subscribe(pred => {
      this.predictionDone.emit(pred);
    });
  }

  getPredictionText(): string {
    const latest_pred: Prediction = this.model.predictions[this.model.predictions.length - 1];
    const directionMap = new Map<PredictionResult, string>([
      [PredictionResult.STRONG_BUY, "go UP by more than 5%"],
      [PredictionResult.BUY, "go UP by more than 1%"],
      [PredictionResult.HOLD, "STAGNATE with less than 1% change"],
      [PredictionResult.SELL, "go DOWN by more than 1%"],
      [PredictionResult.STRONG_SELL, "go DOWN by more than 5%"],
    ]);
    const direction = directionMap.get(latest_pred.result);
    const d = formatDate(latest_pred.created, "dd/MM/yyyy", "en-US");

    const predictionWindowMap = new Map<PredictionWindow, string>([
      [PredictionWindow.TINY, 'day'],
      [PredictionWindow.SMALL, '7 days'],
      [PredictionWindow.MEDIUM, '15 days']
    ]);
    const predWindow = predictionWindowMap.get(this.model.prediction_window);

    // todo: implement in HTML
    return `Based on the latest prediction (${d}) ${this.model.symbol_name} is expected to ${direction} in the following
    ${predWindow} with a confidence level of ${(latest_pred.confidence * 100).toFixed(2)}.`;
  }

  /**
   * Triggered on train model button pressed. Opens dialog for model training
   */
  beforeTrainModel(): void {
    // bars needed for data interval selection step
    this.barService.getBarsBySymbol(this.dataSource, this.model.symbol_name).pipe(take(1)).subscribe(bars => {
      const dialogRef = this._dialog.open(ModelDialogStepperComponent, {
        data: {
          start: bars[0].day,
          end: bars[bars.length - 1].day
        }
      });
      dialogRef.afterClosed().pipe(take(1)).subscribe(data => {
        if (data) {
          this.trainModel(data);
        }
      });
    });
  }

  trainModel(data: { dataStart: Date, dataEnd: Date, patience: number }) {
    this.modelService.updateModel("binance", this.model.id, {
      ...data,
      status: NNModelStatus.IN_TRAINING
    }).pipe(take(1)).subscribe()
    this.trainingStarted.emit(this.model.id);
  }
}
