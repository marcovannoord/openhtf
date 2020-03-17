/**
 * Wrapper around Markdown Service
 */
import { Injectable } from '@angular/core';

import { MarkdownService } from 'ngx-markdown';


@Injectable()
export class OpenHTFMarkdownService {
  constructor(private markdownService: MarkdownService) {}

  forStation(station: any) {
    this.markdownService.options = { baseUrl: station.hostPort };
    return this.markdownService;
  }
}
