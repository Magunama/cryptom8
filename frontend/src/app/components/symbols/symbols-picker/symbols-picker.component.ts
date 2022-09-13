import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {Symbol} from "../../../models/symbol.model";
import {map, Observable, startWith} from "rxjs";
import {FormControl} from "@angular/forms";
import {MatChipInputEvent} from "@angular/material/chips";
import {MatAutocompleteSelectedEvent} from "@angular/material/autocomplete";
import {TouchedSymbol} from "../symbols-page/symbols-page.component";

@Component({
  selector: 'app-symbols-picker',
  templateUrl: './symbols-picker.component.html',
  styleUrls: ['./symbols-picker.component.scss']
})
export class SymbolsPickerComponent implements OnInit {

  private _symbols: Symbol[] = [];

  @Input()
  get symbols() {
    return this._symbols;
  }

  set symbols(symbols: Symbol[]) {
    this._symbols = symbols

    // apply filtering to symbolPickerInput
    this.filteredSymbols = this.symbolPickerInput.valueChanges.pipe(
      startWith(null),
      map((symbol: string | null) => this._pickerFilter(symbol).map(sb => sb.name)),
    );

    this.refreshDisabled = false;
  }

  @Output() symbolSelectedEvent = new EventEmitter<TouchedSymbol>();
  @Output() refreshSymbolsEvent = new EventEmitter();

  touchedSymbols: Map<string, boolean> = new Map<string, boolean>();

  filteredSymbols!: Observable<string[]>;

  symbolPicker = new FormControl();
  symbolPickerInput = new FormControl();

  refreshDisabled: boolean = false;

  constructor() {
  }

  ngOnInit(): void {
  }


  getSelectedSymbolNames(): string[] {
    return this.getSelectedSymbols().map(symbol => symbol.name);
  }

  getSelectedSymbols(): Symbol[] {
    return this.symbols.filter(symbol => symbol.selected);
  }


  /**
   * Return whether a string represents a valid symbol name
   * @param symbolName
   */
  private _validSymbol(symbolName: string): boolean {
    return this.symbols.some(symbol => symbol.name === symbolName);
  }

  addKeywordFromInput(event: MatChipInputEvent) {
    if (event.value && this._validSymbol(event.value)) {
      let symbol: Symbol = this.symbols.filter(symb => symb.name === event.value)[0];
      symbol.selected = true;
      this.touchedSymbols.set(symbol.name, true);

      event.chipInput.clear();
    }
  }

  removeKeyword(keyword: string) {
    let symbol: Symbol = this.symbols.filter(symb => symb.name === keyword)[0];
    symbol.selected = false;
    this.touchedSymbols.set(symbol.name, false);
  }

  onSymbolSelected(event: MatAutocompleteSelectedEvent, symbolPickerInputValue: HTMLInputElement): void {
    let symbol: Symbol = this.symbols.filter(symb => symb.name === event.option.viewValue)[0];
    symbol.selected = true;
    this.touchedSymbols.set(symbol.name, true);

    symbolPickerInputValue.value = "";
    this.symbolPickerInput.setValue(null);
  }

  /**
   * Return filtered symbol array excluding already selected symbols
   * @param value
   */
  private _pickerFilter(value: string | null): Symbol[] {
    if (value === null) {
      // only remove duplicate suggestions
      return this.symbols.filter(symbol => !symbol.selected).slice(0, 20);
    }

    const filterValue = value.toLowerCase();
    return this.symbols.filter(symbol => !symbol.selected &&
      symbol.name.toLowerCase().includes(filterValue)).slice(0, 20);
  }


  refreshSymbols() {
    this.refreshDisabled = true;
    this.refreshSymbolsEvent.emit();
  }

  saveSelectedSymbols() {
    this.symbolPicker.disable();

    if (this.touchedSymbols.size === 0) {
      return;
    }

    this.touchedSymbols.forEach((selected, symbolName, _map) =>
      this.symbolSelectedEvent.emit({selected, symbolName})
    );

    this.touchedSymbols.clear();
  }
}
