import {Component, Input, OnInit} from '@angular/core';
import {FormControl} from "@angular/forms";
import {NNAlgorithm, NNModelStatus} from "../../../models/nnmodel.model";
import {PredictionResult} from "../../../models/prediction.model";

@Component({
  selector: 'app-history-selector',
  templateUrl: './history-selector.component.html',
  styleUrls: ['./history-selector.component.scss']
})
export class HistorySelectorComponent implements OnInit {

  @Input() symbols!: string[];
  algorithmIds: number[] = [...Array(Object.keys(NNAlgorithm).length / 2).keys()];
  resultIds: number[] = [...Array(Object.keys(PredictionResult).length / 2).keys()];

  selectedSymbols = new FormControl('');
  selectedAlgorithms = new FormControl('');
  selectedResults = new FormControl('');

  constructor() {
  }

  ngOnInit(): void {
  }

  resultIdToEnumName(resultId: number | string | undefined): string | undefined {
    if (resultId === undefined) {
      return undefined;
    }

    if (typeof resultId === "number") {
      return PredictionResult[resultId];
    }

    const idx: number = parseInt(resultId);
    return PredictionResult[idx];
  }

  algorithmIdToEnumName(algorithmId: number | string | undefined): string | undefined {
    if (algorithmId === undefined) {
      return undefined;
    }

    if (typeof algorithmId === "number") {
      return NNAlgorithm[algorithmId];
    }

    const idx: number = parseInt(algorithmId);
    return NNAlgorithm[idx];
  }

}
