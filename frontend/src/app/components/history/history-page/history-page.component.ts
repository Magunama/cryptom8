import {Component, OnInit} from '@angular/core';
import {Prediction, PredictionResult} from "../../../models/prediction.model";
import {PredictionService} from "../../../services/prediction.service";
import {ModelService} from "../../../services/model.service";
import {take} from "rxjs";

@Component({
  selector: 'app-history-page',
  templateUrl: './history-page.component.html',
  styleUrls: ['./history-page.component.scss']
})
export class HistoryPageComponent implements OnInit {
  dataSource: string = "binance";
  predictions: Prediction[] = [];

  predictionResultEnum: typeof PredictionResult = PredictionResult;

  constructor(private predictionService: PredictionService, private modelService: ModelService) {
    this.loadPredictions();
  }

  loadPredictions(): void {
    // this.predictionService.getPredictions(this.dataSource).pipe(take(1)).subscribe(preds => {
    //   this.predictions = preds;
    // })

    // todo: remove the need of fetching models
    this.predictions = [];
    this.modelService.getModels(this.dataSource).pipe(take(1)).subscribe(ms => {
      ms.forEach(m => {
        m.predictions.forEach(p => p.symbolName = m.symbol_name);
        this.predictions.push(...m.predictions);
      });
      // todo: fix sorting
      this.predictions.sort((a, b) => {
        if (a.created > b.created) {
          return -1;
        }

        if (a.created < b.created) {
          return 1;
        }

        return 0;
      })
    });


  }

  ngOnInit(): void {
  }

  onSelectedIndexChange(selectedIndex: number) {
    this.dataSource = selectedIndex === 0 ? "binance" : "yfinance";
    this.loadPredictions();
  }
}
