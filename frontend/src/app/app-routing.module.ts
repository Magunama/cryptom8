import {Injectable, NgModule} from '@angular/core';
import {RouterModule, RouterStateSnapshot, Routes, TitleStrategy} from '@angular/router';
import {ModelPageComponent} from "./components/models/model-page/model-page.component";
import {SymbolsPageComponent} from "./components/symbols/symbols-page/symbols-page.component";
import {Title} from "@angular/platform-browser";
import {HistoryPageComponent} from "./components/history/history-page/history-page.component";

const routes: Routes = [
  {path: 'symbols', component: SymbolsPageComponent, title: 'Symbols Page'},
  {path: 'models', component: ModelPageComponent, title: 'Models Page'},
  {path: 'history', component: HistoryPageComponent, title: 'History Page'},
  {path: '', redirectTo: 'symbols', pathMatch: 'full'},
  {path: '**', redirectTo: 'symbols'}

];

@Injectable()
export class TemplatePageTitleStrategy extends TitleStrategy {
  constructor(private readonly title: Title) {
    super();
  }

  override updateTitle(routerState: RouterStateSnapshot) {
    const title = this.buildTitle(routerState);
    if (title !== undefined) {
      this.title.setTitle(`CryptoM8 | ${title}`);
    }
  }
}

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
  providers: [{provide: TitleStrategy, useClass: TemplatePageTitleStrategy}]
})
export class AppRoutingModule {
}
