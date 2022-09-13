import {Component, Input, OnInit, ViewChild} from '@angular/core';

import {ApexAxisChartSeries, ApexChart, ApexTitleSubtitle, ApexXAxis, ApexYAxis, ChartComponent} from "ng-apexcharts";
import {Bar} from "../../models/bar.model";

export type ChartOptions = {
  series: ApexAxisChartSeries;
  chart: ApexChart;
  xaxis: ApexXAxis;
  yaxis: ApexYAxis;
  title: ApexTitleSubtitle;
};

@Component({
  selector: 'app-candlestick',
  templateUrl: './candlestick.component.html',
  styleUrls: ['./candlestick.component.scss']
})
export class CandlestickComponent implements OnInit {
  private _bars!: Bar[];

  @Input()
  get bars() {
    return this._bars;
  }

  set bars(bars: Bar[]) {
    this._bars = bars;

    this.chartOptions.series = CandlestickComponent.getSeries(this.bars);
  }

  @ViewChild("chart", {static: true}) chart!: ChartComponent;
  public chartOptions!: ChartOptions;


  constructor() {
    this.chartOptions = {
      series: CandlestickComponent.getSeries(this.bars),
      chart: {
        type: "candlestick",
        height: 350,
        animations: {
          enabled: false,
        }
      },
      title: {
        text: "CandleStick Chart",
        align: "left"
      },
      xaxis: {
        type: "datetime"
      },
      yaxis: {
        tooltip: {
          enabled: true
        }
      }
    };
  }


  ngOnInit(): void {
  }

  private static getSeries(bars: Bar[]): ApexAxisChartSeries {
    if (bars === undefined || bars.length === 0) {
      return [{name: "candle", data: []}];
    }
    return [{
      name: "candle", data: bars.map((bar: Bar) => ({
        x: bar.day,
        y: [bar.open, bar.high, bar.low, bar.close]
      }))
    }]
  }
}
