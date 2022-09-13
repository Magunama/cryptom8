import {Component, Input, OnInit} from '@angular/core';
import {Title} from "@angular/platform-browser";

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent implements OnInit {
  @Input()
  title!: string;

  constructor(private titleService: Title) {
  }

  ngOnInit(): void {
  }

  getTitle(): string {
    return this.titleService.getTitle();
  }

}
