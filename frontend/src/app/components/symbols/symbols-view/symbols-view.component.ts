import {Component, Input, OnInit} from '@angular/core';
import {Symbol} from "../../../models/symbol.model";
import {MatTableDataSource} from "@angular/material/table";
import {Bar} from "../../../models/bar.model";
import {animate, state, style, transition, trigger} from "@angular/animations";
import {BarService} from "../../../services/bar.service";
import {take} from "rxjs";
import {ModelService} from "../../../services/model.service";
import {Router} from "@angular/router";
import {MatSnackBar} from "@angular/material/snack-bar";
import {MatDialog} from "@angular/material/dialog";
import {SymbolsDialogStepperComponent} from "../symbols-dialog-stepper/symbols-dialog-stepper.component";

@Component({
  selector: 'app-symbols-view',
  templateUrl: './symbols-view.component.html',
  styleUrls: ['./symbols-view.component.scss'],
  animations: [
    trigger('detailExpand', [
      state('collapsed', style({height: '0px', minHeight: '0'})),
      state('expanded', style({height: '*'})),
      transition('expanded <=> collapsed', animate('225ms cubic-bezier(0.4, 0.0, 0.2, 1)'))
    ]),
  ],
})
export class SymbolsViewComponent implements OnInit {
  private _selectedSymbols!: Symbol[];

  @Input()
  get selectedSymbols() {
    return this._selectedSymbols;
  }

  set selectedSymbols(selectedSymbols: Symbol[]) {
    this._selectedSymbols = selectedSymbols;
    this.tableDataSource = new MatTableDataSource<Symbol>(this._selectedSymbols);
  }

  @Input() dataSource!: string;

  displayedColumns: string[] = ['name'];
  tableDataSource = new MatTableDataSource<Symbol>();
  expandedElement!: null | Symbol;
  expandedElementBarsLoading: boolean = true;
  expandedElementBars: Bar[] = [];

  // barsShown: boolean = false;

  constructor(private barService: BarService, private modelService: ModelService, private router: Router,
              private _snackBar: MatSnackBar, private _dialog: MatDialog) {
  }

  ngOnInit(): void {
  }

  getBarsBySymbol(symbol: Symbol): void {
    this.expandedElementBarsLoading = true;
    this.barService.getBarsBySymbol(this.dataSource, symbol.name).pipe(take(1)).subscribe(bars => {
      this.expandedElementBars = bars;
      this.expandedElementBarsLoading = false;
    });
  }

  fetchBarsBySymbol(symbol: Symbol): void {
    this.expandedElementBarsLoading = true;
    this.barService.fetchBarsBySymbol(this.dataSource, symbol.name).pipe(take(1)).subscribe(bars => {
      this.expandedElementBars = bars;
      this.expandedElementBarsLoading = false;
    });
  }


  applyTableFilter(event: Event) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.tableDataSource.filter = filterValue.trim().toLowerCase();
  }


  onExpandedElement(element: Symbol) {
    if (this.expandedElement === element) {
      // this.expandedElement = null;
      return;
    }

    this.expandedElement = element;
    // this.barsShown = false;
    this.getBarsBySymbol(element);
  }

  /**
   * Triggered on create model button pressed. Opens dialog for model creation
   */
  beforeCreateModel(): void {
    const dialogRef = this._dialog.open(SymbolsDialogStepperComponent);
    dialogRef.afterClosed().pipe(take(1)).subscribe(data => {
      if (data) {
        this.createModel(data);
      }
    });
  }

  createModel(data: { algorithm: number, predictionWindow: number }): void {
    // create model from data
    // todo: maybe move this call in parent
    this.modelService.createModel(this.dataSource, this.expandedElement!.name, data.algorithm, data.predictionWindow)
      .pipe(take(1)).subscribe(() => {
        const snackBarRef = this._snackBar.open("Model created!", "View", {duration: 3000});
        snackBarRef.onAction().pipe(take(1)).subscribe(() => {
          this.router.navigateByUrl("/models");
        });
      }
    );
  }

  downloadBarData() {
    this.barService.downloadBars(this.dataSource, this.expandedElement?.name!, this.expandedElementBars);
  }
}
