import {Injectable} from "@angular/core";
import {map, Observable} from "rxjs";
import {HttpClient} from "@angular/common/http";
import {environment} from "../../environments/environment";
import {Bar} from "../models/bar.model";
import {saveAs} from "file-saver";

@Injectable({
  providedIn: 'root',
})
export class BarService {
  constructor(private http: HttpClient) {
  }

  private static makeUrl(dataSource: string): string {
    return `${environment.baseUrl}/${dataSource}/bars`;
  }

  private static convertBarsDates(bars: Bar[]): Bar[] {
    return bars.map(bar => {
      bar.day = new Date(bar.day);
      return bar;
    });
  }

  getBarsBySymbol(dataSource: string, symbolName: string): Observable<Bar[]> {
    return this.http.get<Bar[]>(`${BarService.makeUrl(dataSource)}/${symbolName}`)
      .pipe(map(BarService.convertBarsDates))
  }

  fetchBarsBySymbol(dataSource: string, symbolName: string): Observable<Bar[]> {
    return this.http.get<Bar[]>(`${BarService.makeUrl(dataSource)}/${symbolName}`, {params: {fetch: true}})
      .pipe(map(BarService.convertBarsDates));
  }

  downloadBars(dataSource: string, symbolName: string, bars: Bar[]) {
    const replacer = (_key: any, value: any) => value === null ? '' : value; // specify how you want to handle null values here
    const header = Object.keys(bars[0]);

    type BarKey = keyof Bar;
    let csv = bars.map(row => header.map(fieldName => JSON.stringify(row[fieldName as BarKey], replacer)).join(','));
    csv.unshift(header.join(','));
    let csvArray = csv.join('\r\n');

    const blob = new Blob([csvArray], {type: 'text/csv'})
    saveAs(blob, `${dataSource}-${symbolName}-data.csv`);
  }

}
