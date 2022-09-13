import {Injectable} from "@angular/core";
import {Observable} from "rxjs";
import {HttpClient} from "@angular/common/http";
import {environment} from "../../environments/environment";
import {Symbol} from "../models/symbol.model";

@Injectable({
  providedIn: 'root',
})
export class SymbolService {
  constructor(private http: HttpClient) {
  }

  private static makeUrl(dataSource: string): string {
    return `${environment.baseUrl}/${dataSource}/symbols`;
  }

  getSymbols(dataSource: string): Observable<Symbol[]> {
    return this.http.get<Symbol[]>(SymbolService.makeUrl(dataSource));
  }

  fetchSymbols(dataSource: string): Observable<Symbol[]> {
    return this.http.get<Symbol[]>(SymbolService.makeUrl(dataSource), {params: {fetch: true}});
  }

  updateSymbolSelected(dataSource: string, symbolName: string, selected: boolean): Observable<Object> {
    return this.http.patch(`${SymbolService.makeUrl(dataSource)}/${symbolName}`, {selected: selected});
  }

}
