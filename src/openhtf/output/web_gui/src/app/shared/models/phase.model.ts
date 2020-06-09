/**
 * A phase of a test.
 *
 * May combine both PhaseDescriptor and PhaseState information from the backend.
 */

import { Attachment } from './attachment.model';
import { Measurement } from './measurement.model';

// Enum values must not overlap between any of the status enums.
// See status-pipes.ts.
export enum PhaseStatus {
  waiting = 3,
  running,
  pass,
  fail,
}

export class PhaseRunOptions {
  type: string;
  depth: number;
}

export class Phase {
  attachments: Attachment[];
  descriptorId: number;
  runOptions: PhaseRunOptions|null;
  endTimeMillis: number|null;
  name: string;
  doc: string;
  docExtended: string|null;
  measurements: Measurement[];
  status: PhaseStatus;
  startTimeMillis: number|null;  // Should only be null if phase is waiting.

  // Using the class as the interface for its own constructor allows us to call
  // the constructor in named-argument style.
  constructor(params) {
    var docLines;
    if (params.doc) docLines = params.doc.split("\n");
    else docLines = []
    params.doc = docLines.length > 0 ? docLines[0] : '';
    params.docExtended = docLines.join("\n");
    Object.assign(this, params);
  }
}
