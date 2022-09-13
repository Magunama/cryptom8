import {Component, OnInit} from '@angular/core';
import {take} from "rxjs";
import {ModelService} from "../../../services/model.service";
import {NNModel, NNModelStatus} from "../../../models/nnmodel.model";
import {Prediction} from "../../../models/prediction.model";

@Component({
  selector: 'app-model-page',
  templateUrl: './model-page.component.html',
  styleUrls: ['./model-page.component.scss']
})
export class ModelPageComponent implements OnInit {
  dataSource: string = "binance";
  models: NNModel[] = [];

  constructor(private modelService: ModelService) {
  }

  ngOnInit(): void {
    this.getModels();
  }

  getModels(): void {
    this.modelService.getModels(this.dataSource).pipe(take(1)).subscribe(models => {
      this.models = models;
    });
  }

  onModelDeleted(modelId: number) {
    this.models = this.models.filter((m: NNModel) => m.id !== modelId);
  }

  onPredictionDone(pred: Prediction) {
    this.models.find(m => m.id === pred.model_id)?.predictions.push(pred);
  }

  onSelectedIndexChange(selectedIndex: number) {
    this.dataSource = selectedIndex === 0 ? "binance" : "yfinance";
    this.getModels();
  }

  onTrainingStarted(modelId: number) {
    // todo: maybe refetch model?
    const model: NNModel | undefined = this.models.find(m => m.id === modelId);
    if (model === undefined) {
      return;
    }
    model.status = NNModelStatus.IN_TRAINING;
  }

  /**
   * Returns a set of symbols used in model filtering
   */
  getModelSymbols(): string[] {
    return [... new Set(this.models.map(m => m.symbol_name))];
  }
}
