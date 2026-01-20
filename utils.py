from fastapi import UploadFile, HTTPException

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

async def validate_file_size(file: UploadFile, max_size: int = MAX_FILE_SIZE):
    """
    Validates the size of the uploaded file without reading it into memory.
    Raises HTTPException(413) if file is too large.
    """
    try:
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

        if file_size > max_size:
             raise HTTPException(status_code=413, detail=f"File too large. Maximum size is {max_size // (1024 * 1024)}MB.")
    except Exception as e:
        # If any file operation fails, we should handle it gracefully or re-raise if it's our exception
        if isinstance(e, HTTPException):
            raise e
        # For other IO errors during seek/tell, we might want to log or raise 400
        # But failing open is bad, failing closed is safe.
        # Here we just re-raise if it's not our size check error.
        raise
