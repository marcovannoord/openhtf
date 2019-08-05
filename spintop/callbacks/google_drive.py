import logging
import gspread
import datetime

from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build

SCOPE = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

_LOG = logging.getLogger(__name__)


class FileNotFound(Exception): pass
    

class GoogleDriveWrapper(object):
    def __init__(self, credentials):
        self.service = build('drive', 'v3', credentials=credentials)
        self.gc = gspread.authorize(credentials)

    def print_files(self):
        results = self.service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name, webViewLink)").execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print(u'{0} ({1})'.format(item['name'], item['id']))

    def get_or_create_folder(self, name, share_with=[]):
        folder = None
        try:
            folder_id = self.find_folder(name)
        except FileNotFound:
            folder_id = self.create_folder(name)
        permissions = self.service.permissions().list(fileId=folder_id, fields="permissions(emailAddress)").execute()['permissions']
        current_email_addresses = [perm['emailAddress'] for perm in permissions]
        for email in share_with:
            if email not in current_email_addresses:
                self.share_folder(folder_id, email)
        return folder_id


    def find_folder(self, folder_name):
        response = self.service.files().list(q="mimeType='application/vnd.google-apps.folder' and name='%s'" % folder_name,
                                          spaces='drive',
                                          fields='files(id, name)').execute()
        for f in response.get('files', []):
            return f['id']
        else:
            raise FileNotFound(folder_name)

    def create_folder(self, folder_name, parent_id = None):
        # Create a folder on Drive, returns the newely created folders ID
        body = {
          'name': folder_name,
          'mimeType': "application/vnd.google-apps.folder"
        }
        if parent_id:
            body['parents'] = [parent_id]
        root_folder = self.service.files().create(body = body).execute()
        return root_folder['id']

    def move_file_to_folder(self, file_id, folder_id):
        # Retrieve the existing parents to remove
        file = self.service.files().get(fileId=file_id,
                                        fields='parents').execute()
        previous_parents = ",".join(file.get('parents'))
        # Move the file to the new folder
        file = self.service.files().update(fileId=file_id,
                                            addParents=folder_id,
                                            removeParents=previous_parents,
                                            fields='id, parents').execute()

    def find_filename_in_folder(self, filename, folder_id):
        q = "name='%s'" % filename
        if folder_id:
            q = ("'%s' in parents and " % folder_id) + q

        response = self.service.files().list(q=q,
                                          spaces='drive',
                                          fields='files(id, name)').execute()
        for f in response.get('files', []):
            return f['id']
        else:
            raise FileNotFound('%s in %s' % (filename, folder_id))


    def share_folder(self, folder_id, email):
        def callback(request_id, response, exception):
            if exception:
                # Handle error
                print(exception)
            else:
                print("Permission Id: %s" % response.get('id'))

        batch = self.service.new_batch_http_request(callback=callback)
        user_permission = {
            'type': 'user',
            'role': 'writer',
            'emailAddress': email
        }
        batch.add(self.service.permissions().create(
                fileId=folder_id,
                body=user_permission,
                fields='id',
        ))
        batch.execute()

    def get_or_create_spreadsheet(self, filename, folder_id=None):
        try:
            file_id = self.find_filename_in_folder(filename, folder_id)
            spreadsheet = self.gc.open_by_key(file_id)
        except FileNotFound:
            spreadsheet = self.gc.create(filename)
            if folder_id:
                self.move_file_to_folder(spreadsheet.id, folder_id)
        
        return spreadsheet
            


class GoogleDriveOutput(object):
    INDEX_FILE = 'index'

    def __init__(self, credentials_file, folder_name=None, share_with=[]):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, SCOPE)
        
        self.sheet = None
        # if spreadsheet_name:
        #     self.create_file(spreadsheet_name, share_with=share_with)
        
        self.gwrap = GoogleDriveWrapper(credentials)
        # self.gwrap.print_files()
        self.folder_id = self.gwrap.get_or_create_folder(folder_name, share_with=share_with)

        self.addons = [
            TestRecordToSheetAddon(self.gwrap, self.folder_id),
            TestRecordToRowAddon(self.gwrap, self.INDEX_FILE, self.folder_id)
        ]


    def create_file(self, name, share_with=[]):
        try:
            self.spreadsheet = self.gc.open(name)
            _LOG.info('Opened test results spreadsheet named %s' % name)
        except:
            self.spreadsheet = self.gc.create(name)
            _LOG.info('Created test results spreadsheet named %s' % name)

        shared_emails = [shared['emailAddress'] for shared in self.spreadsheet.list_permissions()]

        for email in share_with:
            if email not in shared_emails:
                self.spreadsheet.share(email, perm_type='user', role='writer')
        self.sheet = self.spreadsheet.get_worksheet(0)
        return self.sheet

    def __call__(self, test_record):
        for addon in self.addons:
            addon(test_record)

    def get_header(self):
        return [col[0] for col in self.COLUMNS]

    def get_values(self, tr):
        return [col[1](tr) for col in self.COLUMNS]

class TestRecordToSheetAddon(object):
    PHASE_COLUMNS = [
        ('name', lambda phase: phase.name),
        ('start_time', lambda phase: str(millis_to_datetime(phase.start_time_millis))),
        ('end_time', lambda phase: str(millis_to_datetime(phase.end_time_millis))),
        ('outcome', lambda phase: phase.outcome.name),
    ]

    def __init__(self, gwrap, folder_id=None):
        self.gwrap = gwrap
        self.folder_id = folder_id

    def __call__(self, test_record):
        filename = '{dut_id}-{timestamp}'.format(
            dut_id=test_record.dut_id, 
            timestamp=str(millis_to_datetime(test_record.start_time_millis))
        )
        
        sheet = self.gwrap.get_or_create_spreadsheet(filename, self.folder_id).sheet1
        file_id = sheet.spreadsheet.id
        file_url = 'https://docs.google.com/spreadsheets/d/%s/edit?usp=drivesdk' % file_id
        test_record.metadata['google_sheet_result_file_url'] = file_url

        row_index = next_available_row(sheet)
        sheet.resize(row_index)
        sheet.append_row(self.get_header())
        
        for phase in test_record.phases:
            sheet.append_row(self.get_values(phase), value_input_option='USER_ENTERED')


    def get_header(self):
        return [col[0] for col in self.PHASE_COLUMNS]

    def get_values(self, phase):
        return [col[1](phase) for col in self.PHASE_COLUMNS]

class TestRecordToRowAddon(object):
    INDEX_TESTS_WORKSHEET = 'Tests'
    INDEX_MEASUREMENTS_WORKSHEET = 'Measurements'

    COLUMNS = [
        ('url', lambda tr: get_sheet_url(tr)),
        ('station_id', lambda tr: tr.station_id),
        ('dut_id', lambda tr: tr.dut_id),
        ('start_time', lambda tr: str(millis_to_datetime(tr.start_time_millis))),
        ('end_time', lambda tr: str(millis_to_datetime(tr.end_time_millis))),
        ('outcome', lambda tr: tr.outcome.name),
        ('error', lambda tr: format_error(tr)),
        # ('error', lambda tr: )
    ]

    def __init__(self, gwrap, filename, folder_id=None):
        self.spreadsheet = gwrap.get_or_create_spreadsheet(filename, folder_id)

        self.tests_sheet = self.spreadsheet.get_worksheet(0)
        self.tests_sheet.update_title(self.INDEX_TESTS_WORKSHEET)

        self.measurements_sheet = self.spreadsheet.get_worksheet(1)
        if self.measurements_sheet is None:
            self.measurements_sheet = self.spreadsheet.add_worksheet(title=self.INDEX_MEASUREMENTS_WORKSHEET, rows="1", cols="20")
        else:
            self.measurements_sheet.update_title(self.INDEX_MEASUREMENTS_WORKSHEET)

    def __call__(self, test_record):
        self.add_test_row(test_record)
    
    def add_test_row(self, test_record):
        sheet = self.tests_sheet
        row_index = next_available_row(sheet)
        sheet.resize(row_index)
        if row_index == '1':
            sheet.append_row(self.get_header())
            # write header
        sheet.append_row(self.get_values(test_record), value_input_option='USER_ENTERED')


    def get_header(self):
        return [col[0] for col in self.COLUMNS]

    def get_values(self, tr):
        return [col[1](tr) for col in self.COLUMNS]

def millis_to_datetime(millis):
    return datetime.datetime.fromtimestamp(millis/1000.0)

def next_available_row(worksheet):
    str_list = list(filter(lambda x: bool(x), worksheet.col_values(1)))
    return str(len(str_list)+1)

def format_error(test_record):
    errors = [':'.join(details) for details in test_record.outcome_details]
    return ' AND '.join(errors)

def get_sheet_url(test_record):
    file_url = test_record.metadata['google_sheet_result_file_url']
    return '=HYPERLINK("%s", "Link")' % file_url