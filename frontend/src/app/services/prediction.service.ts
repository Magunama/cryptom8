import {Injectable} from "@angular/core";
import {Observable} from "rxjs";
import {HttpClient} from "@angular/common/http";
import {environment} from "../../environments/environment";
import {NNAlgorithm, NNModel, NNModelStatus} from "../models/nnmodel.model";
import {Prediction} from "../models/prediction.model";

@Injectable({
  providedIn: 'root',
})
export class PredictionService {
  constructor(private http: HttpClient) {
  }

  private static makeUrl(dataSource: string): string {
    return `${environment.baseUrl}/${dataSource}/predictions`;
  }

  getPredictions(dataSource: string): Observable<Prediction[]> {
    return this.http.get<Prediction[]>(PredictionService.makeUrl(dataSource));
  }

  makePrediction(dataSource: string, modelId: number): Observable<Prediction> {
    return this.http.post<Prediction>(`${environment.baseUrl}/${dataSource}/predictions`, {
      model_id: modelId
    });
  }

}

