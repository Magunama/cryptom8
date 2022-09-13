import {Injectable} from "@angular/core";
import {Observable} from "rxjs";
import {HttpClient} from "@angular/common/http";
import {environment} from "../../environments/environment";
import {NNAlgorithm, NNModel, NNModelStatus, PredictionWindow} from "../models/nnmodel.model";

@Injectable({
  providedIn: 'root',
})
export class ModelService {
  constructor(private http: HttpClient) {
  }

  private static makeUrl(dataSource: string): string {
    return `${environment.baseUrl}/${dataSource}/models`;
  }

  getModels(dataSource: string): Observable<NNModel[]> {
    return this.http.get<NNModel[]>(ModelService.makeUrl(dataSource));
  }

  createModel(dataSource: string, symbolName: string, algorithm: NNAlgorithm, predictionWindow: PredictionWindow): Observable<NNModel> {
    return this.http.post<NNModel>(`${ModelService.makeUrl(dataSource)}`, {
      symbol_name: symbolName,
      algorithm: algorithm,
      prediction_window: predictionWindow
    });
  }

  updateModel(dataSource: string, modelId: number, payload: any): Observable<NNModel> {
    return this.http.patch<NNModel>(`${ModelService.makeUrl(dataSource)}/${modelId}`, payload);
  }

  deleteModel(dataSource: string, modelId: number): Observable<NNModel> {
    return this.http.delete<NNModel>(`${ModelService.makeUrl(dataSource)}/${modelId}`);
  }
}
