import {Component, OnInit} from '@angular/core';
import {SymbolService} from "../../../services/symbol.service";
import {BarService} from "../../../services/bar.service";
import {take} from "rxjs";
import {Symbol} from "../../../models/symbol.model";

export interface TouchedSymbol {
  selected: boolean
  symbolName: string
}

@Component({
  selector: 'app-symbols-page',
  templateUrl: './symbols-page.component.html',
  styleUrls: ['./symbols-page.component.scss']
})
export class SymbolsPageComponent implements OnInit {
  dataSource: string = "binance";

  symbols: Symbol[] = [];
  selectedSymbols!: Symbol[];

  constructor(private symbolService: SymbolService, private barService: BarService) {
  }

  ngOnInit(): void {
    this.getSymbols();
  }

  getSymbols(): void {
    // this.symbols = [];
    this.symbolService.getSymbols(this.dataSource).pipe(take(1)).subscribe(symbols => {
      this.symbols = symbols;
      this.selectedSymbols = this.getSelectedSymbols();
    });
  }

  getSelectedSymbols(): Symbol[] {
    return this.symbols.filter(symbol => symbol.selected);
  }

  onSymbolSelected(ts: TouchedSymbol) {
    this.symbolService.updateSymbolSelected(this.dataSource, ts.symbolName, ts.selected).pipe(take(1)).subscribe();
    this.selectedSymbols = this.getSelectedSymbols();
  }

  onSelectedIndexChange(selectedIndex: number) {
    this.dataSource = selectedIndex === 0 ? "binance" : "yfinance";
    this.getSymbols();
  }

  onRefreshSymbols() {
    this.symbolService.fetchSymbols(this.dataSource).pipe(take(1)).subscribe(symbols => this.symbols = symbols);
  }
}
