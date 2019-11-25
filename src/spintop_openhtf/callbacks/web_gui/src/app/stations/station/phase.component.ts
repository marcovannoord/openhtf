/**
 * Widget displaying the phases of a test.
 */

import { Component, Input, SimpleChanges } from '@angular/core';

import { MeasurementStatus } from '../../shared/models/measurement.model';
import { Phase, PhaseStatus } from '../../shared/models/phase.model';

import { MarkdownService } from 'ngx-markdown';
import { DomSanitizer } from '@angular/platform-browser';

@Component({
  selector: 'htf-phase',
  templateUrl: './phase.component.html',
  styleUrls: ['./phase.component.scss'],
})
export class PhaseComponent {
  @Input() phase: Phase;
  @Input() expand: boolean;
  @Input() expandIfRunning: boolean;

  MeasurementStatus = MeasurementStatus;
  PhaseStatus = PhaseStatus;
  docExtended = null;
  
  constructor(private sanitizer: DomSanitizer, private markdownService: MarkdownService) {
  }
  
  ngOnChanges(changes: SimpleChanges) {
    if (changes.phase) {
      this.computeDocExtended()
    }
  }

  computeDocExtended() {
    const doc = this.markdownService.compile(this.phase.docExtended);
    // const safeHtml = this.sanitizer.sanitize(SecurityContext.HTML, doc);
    this.docExtended = this.sanitizer.bypassSecurityTrustHtml(doc);
  }

  get showDocExtended() {
    const shouldShow = this.expand || (this.expandIfRunning && this.phase.status === PhaseStatus.running);
    return shouldShow && this.phase.docExtended;
  }

  get showMeasurements() {
    return this.expand && this.phase.measurements.length > 0;
  }
}
