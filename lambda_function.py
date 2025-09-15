import paramiko
import datetime
import os
from pathlib import Path

def download_folder_contents(sftp, remote_path, local_path, max_files=None):
    """
    Download all files from a remote folder to a local folder
    """
    try:
        # Create local directory if it doesn't exist
        os.makedirs(local_path, exist_ok=True)
        
        # List files in remote directory
        files = sftp.listdir(remote_path)
        
        if max_files:
            files = files[:max_files]
        
        downloaded_count = 0
        failed_count = 0
        
        for file in files:
            try:
                remote_file_path = f"{remote_path}/{file}"
                local_file_path = os.path.join(local_path, file)
                
                # Check if it's a file (not a directory)
                try:
                    file_stat = sftp.stat(remote_file_path)
                    # If stat succeeds and it's not a directory, download it
                    print(f"    Downloading: {file} ({file_stat.st_size} bytes)")
                    sftp.get(remote_file_path, local_file_path)
                    downloaded_count += 1
                    
                except IOError:
                    # Might be a directory, skip it for now
                    print(f"    Skipping (likely directory): {file}")
                    
            except Exception as e:
                print(f"    Failed to download {file}: {str(e)}")
                failed_count += 1
        
        return downloaded_count, failed_count
        
    except Exception as e:
        print(f"Error accessing {remote_path}: {str(e)}")
        return 0, 0

def main():
    try:
        hostname = "s-4847307e654242858.server.transfer.us-east-1.amazonaws.com"
        port = 22
        username = "social.mediateam@dwp.gov.uk"
        password = "LlAdSUdtUSCal0Ja"
        
        # Local base directory for downloads
        local_base_dir = "8_september_downloaded_data"
        os.makedirs(local_base_dir, exist_ok=True)
        
        # Connect
        print("Connecting to SFTP server...")
        transport = paramiko.Transport((hostname, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        print("Connected successfully!")
        
        # Check inside the export folder
        print("\nChecking 'export' folder contents:")
        try:
            export_files = sftp.listdir('export')
            
            if not export_files:
                print("  Export folder is EMPTY - no data files found")
                return
            
            print(f"  Found {len(export_files)} items in export folder")
            export_files.sort(reverse=True)  # Most recent first
            
            # Download options
            download_recent_only = True  # Set to False to download all folders
            max_folders_to_process = 5   # Limit number of folders to process
            max_files_per_folder = 100   # Limit files per folder (None for all)
            
            total_downloaded = 0
            total_failed = 0
            processed_folders = 0
            
            # Process each folder/file
            for item in export_files:
                if processed_folders >= max_folders_to_process:
                    print(f"\nReached limit of {max_folders_to_process} folders. Stopping.")
                    break
                
                # Check if it looks like a date folder (YYYY_MM_DD format)
                if download_recent_only:
                    try:
                        # Try to parse as date folder
                        datetime.datetime.strptime(item, "%Y_%m_%d")
                        is_date_folder = True
                    except ValueError:
                        is_date_folder = False
                        continue  # Skip non-date folders if only downloading recent
                else:
                    is_date_folder = True  # Process all items
                
                if is_date_folder:
                    remote_folder_path = f"export/{item}"
                    local_folder_path = os.path.join(local_base_dir, item)
                    
                    print(f"\n📁 Processing folder: {item}")
                    print(f"   Remote path: {remote_folder_path}")
                    print(f"   Local path: {local_folder_path}")
                    
                    try:
                        # Try to list contents to confirm it's a directory
                        folder_contents = sftp.listdir(remote_folder_path)
                        print(f"   Found {len(folder_contents)} files in folder")
                        
                        if len(folder_contents) > 0:
                            downloaded, failed = download_folder_contents(
                                sftp, remote_folder_path, local_folder_path, max_files_per_folder
                            )
                            total_downloaded += downloaded
                            total_failed += failed
                            processed_folders += 1
                            
                            print(f"   ✓ Downloaded {downloaded} files")
                            if failed > 0:
                                print(f"   ✗ Failed to download {failed} files")
                        else:
                            print(f"   Empty folder, skipping")
                            
                    except Exception as e:
                        print(f"   Error processing folder {item}: {str(e)}")
                        # Might be a file, not a folder
                        try:
                            local_file_path = os.path.join(local_base_dir, item)
                            print(f"   Trying to download as file: {item}")
                            sftp.get(f"export/{item}", local_file_path)
                            total_downloaded += 1
                            print(f"   ✓ Downloaded file: {item}")
                        except Exception as file_error:
                            print(f"   ✗ Failed to download as file: {str(file_error)}")
                            total_failed += 1
        
        except Exception as e:
            print(f"Error accessing export folder: {str(e)}")
        
        finally:
            sftp.close()
            transport.close()
            print(f"\n🏁 Download Summary:")
            print(f"   Processed folders: {processed_folders}")
            print(f"   Total files downloaded: {total_downloaded}")
            print(f"   Total failures: {total_failed}")
            print(f"   Local download directory: {os.path.abspath(local_base_dir)}")
    
    except Exception as e:
        print(f"Connection Error: {str(e)}")

if __name__ == "__main__":
    main()
