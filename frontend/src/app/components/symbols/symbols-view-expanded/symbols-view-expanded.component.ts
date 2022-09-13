import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {Bar} from "../../../models/bar.model";
import {FormControl, FormGroup} from "@angular/forms";
import {last} from "rxjs";

@Component({
  selector: 'app-symbols-view-expanded',
  templateUrl: './symbols-view-expanded.component.html',
  styleUrls: ['./symbols-view-expanded.component.scss']
})
export class SymbolsViewExpandedComponent implements OnInit {
  @Input()
  expandedElementBars!: Bar[];
  barsShown: boolean = false;

  @Output()
  onModelCreation = new EventEmitter();

  @Output()
  onBarDataDownload = new EventEmitter();

  @Output()
  onFetchNewData = new EventEmitter();

  minDate: Date | undefined;
  maxDate: Date | undefined;

  selectedRange = new FormGroup({
    start: new FormControl(),
    end: new FormControl(),
  });

  candlestickBars: Bar[] = [];

  constructor() {
  }

  ngOnInit(): void {
    this.minDate = this.expandedElementBars[0].day;
    this.maxDate = this.expandedElementBars[this.expandedElementBars.length - 1].day;

    this.candlestickBars = this.expandedElementBars.slice(-90);
  }

  // todo: avoid this hack-ish comparison
  private static equalDates(a: Date, b: Date): boolean {
    return a.getDate() === b.getDate() && a.getMonth() === b.getMonth() && a.getFullYear() === b.getFullYear();
  }

  onSeletedDateRangeChange() {
    const selectedStartDate: Date = this.selectedRange.get("start")!.value;
    const selectedEndDate: Date = this.selectedRange.get("end")!.value;

    if (selectedEndDate === null) {
      return;
    }

    // account for different timezone?
    // selectedStartDate.setMinutes(selectedStartDate.getMinutes() - selectedStartDate.getTimezoneOffset());
    // selectedEndDate.setMinutes(selectedEndDate.getMinutes() - selectedEndDate.getTimezoneOffset());

    const selectedStartDateIndex = this.expandedElementBars.findIndex((bar: Bar) =>
      SymbolsViewExpandedComponent.equalDates(bar.day, selectedStartDate));
    const selectedEndDateIndex = this.expandedElementBars.findIndex((bar) =>
      SymbolsViewExpandedComponent.equalDates(bar.day, selectedEndDate));
    this.candlestickBars = this.expandedElementBars.slice(selectedStartDateIndex, selectedEndDateIndex + 1);
  }

  fetchNewDataDisabled(): boolean {
    const todayDate: Date = new Date();
    const today = Date.UTC(todayDate.getUTCFullYear(), todayDate.getUTCMonth(), todayDate.getUTCDate());

    const lastBarDate: Date = this.expandedElementBars[this.expandedElementBars.length - 1].day;
    const lastBar = Date.UTC(lastBarDate.getUTCFullYear(), lastBarDate.getUTCMonth(), lastBarDate.getUTCDate());

    // more than a day has passed since last pulled data
    return Math.floor(today - lastBar) / (1000 * 60 * 60 * 24) <= 0;
  }
}
