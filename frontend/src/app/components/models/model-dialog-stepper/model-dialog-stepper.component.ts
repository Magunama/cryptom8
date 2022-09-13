import {Component, Inject, OnInit} from '@angular/core';
import {FormBuilder, FormControl, FormGroup, Validators} from "@angular/forms";
import {map, Observable} from "rxjs";
import {StepperOrientation} from "@angular/cdk/stepper";
import {BreakpointObserver} from "@angular/cdk/layout";
import {MAT_DIALOG_DATA, MatDialogRef} from "@angular/material/dialog";

interface DialogDataInterval {
  start: Date,
  end: Date,
}

@Component({
  selector: 'app-model-dialog-stepper',
  templateUrl: './model-dialog-stepper.component.html',
  styleUrls: ['./model-dialog-stepper.component.scss']
})
export class ModelDialogStepperComponent implements OnInit {
  firstFormGroup!: FormGroup;

  secondFormGroup = this._formBuilder.group({
    patience: ['', Validators.required],
  });
  patienceLevel: number = 60; //default value

  stepperOrientation: Observable<StepperOrientation>;

  constructor(@Inject(MAT_DIALOG_DATA) public data: DialogDataInterval, private _formBuilder: FormBuilder,
              private _breakpointObserver: BreakpointObserver,
              private _dialogRef: MatDialogRef<ModelDialogStepperComponent>) {
    this.stepperOrientation = _breakpointObserver
      .observe('(min-width: 800px)')
      .pipe(map(({matches}) => (matches ? 'horizontal' : 'vertical')));

    // insert max range as default value
    this.firstFormGroup = this._formBuilder.group({
      start: new FormControl(this.data.start),
      end: new FormControl(this.data.end)
    });
  }


  ngOnInit(): void {
  }

  onStepperSubmit() {
    const start = this.firstFormGroup.get("start")?.value;
    const end = this.firstFormGroup.get("end")?.value;

    // no need to include data interval changes
    if (start === this.data.start && end === this.data.end) {
      this._dialogRef.close({patience: this.patienceLevel});
      return;
    }

    this._dialogRef.close({data_start: start, data_end: end, patience: this.patienceLevel});
  }
}
