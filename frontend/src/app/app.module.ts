import {NgModule} from '@angular/core';
import {BrowserModule} from '@angular/platform-browser';

import {AppRoutingModule} from './app-routing.module';
import {AppComponent} from './app.component';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {MatTabsModule} from "@angular/material/tabs";
import {MatChipsModule} from "@angular/material/chips";
import {FormsModule, ReactiveFormsModule} from "@angular/forms";
import {MatFormFieldModule} from "@angular/material/form-field";
import {MatButtonModule} from "@angular/material/button";
import {MatIconModule} from "@angular/material/icon";
import {MatTableModule} from "@angular/material/table";
import {MatInputModule} from "@angular/material/input";
import {HttpClientModule} from "@angular/common/http";
import {MatAutocompleteModule} from "@angular/material/autocomplete";
import {MatProgressSpinnerModule} from "@angular/material/progress-spinner";
import {ModelPageComponent} from './components/models/model-page/model-page.component';
import {HeaderComponent} from './components/header/header.component';
import {MatToolbarModule} from "@angular/material/toolbar";
import {MatGridListModule} from "@angular/material/grid-list";
import {MatProgressBarModule} from "@angular/material/progress-bar";
import {MatCardModule} from "@angular/material/card";
import {MatDividerModule} from "@angular/material/divider";
import {ModelCardComponent} from './components/models/model-card/model-card.component';
import {CandlestickComponent} from './components/candlestick/candlestick.component';
import {NgApexchartsModule} from "ng-apexcharts";
import {FlexLayoutModule} from "@angular/flex-layout";
import {MatSnackBarModule} from "@angular/material/snack-bar";
import {SymbolsPageComponent} from './components/symbols/symbols-page/symbols-page.component';
import {SymbolsPickerComponent} from './components/symbols/symbols-picker/symbols-picker.component';
import {SymbolsViewComponent} from './components/symbols/symbols-view/symbols-view.component';
import {SymbolsViewExpandedComponent} from './components/symbols/symbols-view-expanded/symbols-view-expanded.component';
import {MatDatepickerModule} from "@angular/material/datepicker";
import {MatNativeDateModule} from "@angular/material/core";
import {MatListModule} from "@angular/material/list";
import {HistoryPageComponent} from './components/history/history-page/history-page.component';
import {MatExpansionModule} from "@angular/material/expansion";
import {
  SymbolsDialogStepperComponent
} from './components/symbols/symbols-dialog-stepper/symbols-dialog-stepper.component';
import {MatDialogModule} from "@angular/material/dialog";
import {MatStepperModule} from "@angular/material/stepper";
import {MatRadioModule} from "@angular/material/radio";
import {MatSlideToggleModule} from "@angular/material/slide-toggle";
import { ModelDialogStepperComponent } from './components/models/model-dialog-stepper/model-dialog-stepper.component';
import { ModelSelectorComponent } from './components/models/model-selector/model-selector.component';
import {MatSelectModule} from "@angular/material/select";
import {MatSliderModule} from "@angular/material/slider";
import {HistorySelectorComponent} from "./components/history/history-selector/history-selector.component";

export const materialModules = [
  MatTabsModule,
  MatChipsModule,
  MatFormFieldModule,
  MatButtonModule,
  MatIconModule,
  MatTableModule,
  MatInputModule,
  MatAutocompleteModule,
  MatToolbarModule,
  MatGridListModule,
  MatProgressBarModule,
  MatCardModule,
  MatDividerModule,
  MatProgressSpinnerModule,
  MatSnackBarModule,
  MatDatepickerModule,
  MatNativeDateModule,
  MatListModule,
  MatExpansionModule,
  MatDialogModule,
  MatStepperModule,
  MatRadioModule,
  MatSlideToggleModule,
  MatSelectModule,
  MatSliderModule
]

@NgModule({
  declarations: [
    AppComponent,
    ModelPageComponent,
    HeaderComponent,
    ModelCardComponent,
    CandlestickComponent,
    SymbolsPageComponent,
    SymbolsPickerComponent,
    SymbolsViewComponent,
    SymbolsViewExpandedComponent,
    HistoryPageComponent,
    SymbolsDialogStepperComponent,
    ModelDialogStepperComponent,
    ModelSelectorComponent,
    HistorySelectorComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    ReactiveFormsModule,
    FormsModule,
    HttpClientModule,
    ...materialModules,
    NgApexchartsModule,
    FlexLayoutModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule {
}
