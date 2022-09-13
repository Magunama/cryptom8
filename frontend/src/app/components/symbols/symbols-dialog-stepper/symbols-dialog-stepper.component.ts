import {Component, OnInit} from '@angular/core';
import {FormBuilder, Validators} from "@angular/forms";
import {map, Observable} from "rxjs";
import {StepperOrientation} from "@angular/cdk/stepper";
import {BreakpointObserver} from "@angular/cdk/layout";
import {BaseNNAlgorithm, PredictionWindow} from "../../../models/nnmodel.model";
import {MatDialogRef} from "@angular/material/dialog";

@Component({
  selector: 'app-models-dialog-stepper',
  templateUrl: './symbols-dialog-stepper.component.html',
  styleUrls: ['./symbols-dialog-stepper.component.scss']
})
export class SymbolsDialogStepperComponent implements OnInit {
  firstFormGroup = this._formBuilder.group({
    selectAlgorithm: ['', Validators.required],
  });

  baseAlgorithmsLength = Object.keys(BaseNNAlgorithm).length / 2
  algorithmIds: number[] = [...Array(this.baseAlgorithmsLength).keys()];
  algorithmEnum: typeof BaseNNAlgorithm = BaseNNAlgorithm;


  secondFormGroup = this._formBuilder.group({
    selectPredictionWindow: ['', Validators.required],
  });
  predictionWindowIds: number[] = [...Array(Object.keys(PredictionWindow).length / 2).keys()];
  predictionWindowEnum: typeof PredictionWindow = PredictionWindow;


  thirdFormGroup = this._formBuilder.group({
    enableSequencing: ['', Validators.required],
  });

  stepperOrientation: Observable<StepperOrientation>;

  constructor(private _formBuilder: FormBuilder, private _breakpointObserver: BreakpointObserver,
              private _dialogRef: MatDialogRef<SymbolsDialogStepperComponent>) {
    this.stepperOrientation = _breakpointObserver
      .observe('(min-width: 800px)')
      .pipe(map(({matches}) => (matches ? 'horizontal' : 'vertical')));
  }


  ngOnInit(): void {
  }

  onStepperSubmit() {
    const algorithmValue = this.firstFormGroup.get("selectAlgorithm")!.value;
    const predictionWindowValue = this.secondFormGroup.get("selectPredictionWindow")!.value;
    const sequencingValue = this.thirdFormGroup.get("enableSequencing")!.value;

    // this will probably never happen, but for validation purposes
    if (algorithmValue === null || predictionWindowValue === null) {
      this._dialogRef.close();
      return;
    }

    let algorithm = parseInt(algorithmValue);
    if (sequencingValue !== "") {
      algorithm += this.baseAlgorithmsLength;
    }
    const predictionWindow = parseInt(predictionWindowValue);
    this._dialogRef.close({algorithm, predictionWindow})
  }
}
