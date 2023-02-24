from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from flask import Flask, request, jsonify, render_template, make_response
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

app = Flask(__name__)

# Set the path to the service account key file
service_account_file = "C:/Users\sahus\Downloads\cloud-storage-378305-aab12c589e0a.json"

# Authenticate with the Google Drive API using the service account
creds = service_account.Credentials.from_service_account_file(service_account_file, scopes=['https://www.googleapis.com/auth/drive'])
drive_service = build('drive', 'v3', credentials=creds)

@app.route('/', methods=['GET'])
def home():
    return render_template('drive.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    # save the uploaded file to a temporary location on the server
    file_path = file.filename
    file.save(file_path)
    file_metadata = {'name': file.filename}
    media = MediaFileUpload(file_path, resumable=True)
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return jsonify({'file_id': file.get('id')})

@app.route('/download', methods=['GET'])
def download_file():
    file_id = request.args.get('file_id')
    file = drive_service.files().get(fileId=file_id).execute()
    file_name = file.get('name')
    file_stream = io.BytesIO()
    downloader = MediaIoBaseDownload(file_stream, drive_service.files().get_media(fileId=file_id))
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    file_stream.seek(0)
    response = make_response(file_stream.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename={file_name}'
    return response

if __name__ == '__main__':
    app.run(debug=True)
