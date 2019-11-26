/**
 * Component representing the UserInput plug.
 */

import { trigger } from '@angular/animations';

import { Component, ElementRef } from '@angular/core';
import { Http } from '@angular/http';
import { DomSanitizer } from '@angular/platform-browser';

import { ConfigService } from '../core/config.service';
import { FlashMessageService } from '../core/flash-message.service';
import { washIn } from '../shared/animations';

import { MarkdownService } from 'ngx-markdown';

import { BasePlug } from './base-plug';

const plugName = 'openhtf.plugs.user_input.UserInput';

export declare interface UserInputPlugState {
  default?: string;  // Used by ui_plugs.advanced_user_input.AdvancedUserInput.
  error?: string;    // Used by ui_plugs.advanced_user_input.AdvancedUserInput.
  id: string;
  message: string;
  prompt_type: string;
  options: Array<object>;
}

class PromptData {
  lastId: string;
  data: any;

  hasChanged(state) {
    return state.id !== this.lastId;
  }
}

@Component({
  animations: [trigger('animateIn', washIn)],
  selector: 'htf-user-input-plug',
  templateUrl: './user-input-plug.component.html',
  styleUrls: ['./user-input-plug.component.scss'],
})
export class UserInputPlugComponent extends BasePlug {
  private lastPromptHtml: PromptData;
  private lastPromptForm: PromptData;

  private response: any;

  constructor(
      config: ConfigService, http: Http, flashMessage: FlashMessageService,
      private ref: ElementRef, private sanitizer: DomSanitizer, 
      private markdownService: MarkdownService) {
    super(plugName, config, http, flashMessage);
  }

  get isForm() {
    return Boolean(this.lastPromptForm && this.lastPromptForm.data);
  }

  get error() {
    return this.getPlugState().error;
  }

  get options() {
    return this.getPlugState().options;
  }

  formContentChanged(data) {
    this.response = data;
  }

  get promptForm() {
    this.lastPromptForm = this._genericPrompt(this.lastPromptForm, 
      (content) => {
        if (typeof content === 'object') {
          return {
            options: {addSubmit: false},
            ...content
          };
        }
        else return null;
      }
    )
    return this.lastPromptForm.data;
  }

  get promptHtml() {
    this.lastPromptHtml = this._genericPrompt(this.lastPromptHtml, 
      (message) => {
        var value;
        if (typeof message === 'object') {
          value = '';
        }
        else {
          const markdown = this.markdownService; //.forStation(this.test.station);
          message = markdown.compile(message.toString())
          // const safeHtml = this.sanitizer.sanitize(SecurityContext.HTML, message)
                  // .replace(/&#10;/g, '<br>');  // Convert newlines.
          value = this.sanitizer.bypassSecurityTrustHtml(message);
        }
        return value;
      }
    )
    return this.lastPromptHtml.data;
  }

  _genericPrompt(dataObject, onChange) {
    const state = this.getPlugState();

    if (!dataObject) dataObject = new PromptData();

    if (dataObject.hasChanged(state)) {
      this.response = null;
      dataObject.lastId = state.id;
      dataObject.data = onChange(state.message)
      this.focusSelf()
    }
    return dataObject
  }

  sendResponse(optionKey: string|null) {
    if (optionKey === null) optionKey = this.options[0]['key'];

    const promptId = this.getPlugState().id;
    let response;

    if (this.response) {
      response = this.response;
    } else {
      response = {};
    }
    const response_data = {
      content: response,
      option: optionKey
    }

    this.respond('respond', [promptId, response_data]);
  }

  protected getPlugState() {
    return super.getPlugState() as UserInputPlugState;
  }

  private focusSelf() {
    const input = this.ref.nativeElement.querySelector('json-schema-form');
    if (input) {
      input.focus();
    }
  }
}
