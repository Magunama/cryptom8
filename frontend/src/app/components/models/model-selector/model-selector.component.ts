import {Component, Input, OnInit} from '@angular/core';
import {FormControl} from "@angular/forms";
import {NNAlgorithm, NNModelStatus} from "../../../models/nnmodel.model";

@Component({
  selector: 'app-model-selector',
  templateUrl: './model-selector.component.html',
  styleUrls: ['./model-selector.component.scss']
})
export class ModelSelectorComponent implements OnInit {

  @Input() symbols!: string[];
  algorithmIds: number[] = [...Array(Object.keys(NNAlgorithm).length / 2).keys()];
  statusIds: number[] = [...Array(Object.keys(NNModelStatus).length / 2).keys()];

  selectedSymbols = new FormControl('');
  selectedAlgorithms = new FormControl('');
  selectedStatuses = new FormControl('');

  constructor() {
  }

  ngOnInit(): void {
  }

  statusIdToEnumName(statusId: number | string | undefined): string | undefined {
    if (statusId === undefined) {
      return undefined;
    }

    if (typeof statusId === "number") {
      return NNModelStatus[statusId];
    }

    const idx: number = parseInt(statusId);
    return NNModelStatus[idx];
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
