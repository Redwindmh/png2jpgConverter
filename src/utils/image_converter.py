import os
from PIL import Image as PILImage

def convert_image(file_path, output_dir, width=None, height=None):
    """
    Convert a single PNG image to JPG format.
    
    Args:
        file_path (str): Path to the input PNG file
        output_dir (str): Directory to save the output JPG file
        width (int, optional): Target width for resizing
        height (int, optional): Target height for resizing
        
    Returns:
        str: Path to the converted file
    """
    try:
        # Open and convert image
        with PILImage.open(file_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA'):
                background = PILImage.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize if specified
            if width and height:
                img = img.resize((width, height), PILImage.Resampling.LANCZOS)
            
            # Save as JPG
            output_path = os.path.join(
                output_dir,
                os.path.splitext(os.path.basename(file_path))[0] + '.jpg'
            )
            img.save(output_path, 'JPEG', quality=95)
            return output_path
    except Exception as e:
        raise Exception(f'Error converting {file_path}: {str(e)}')

def ensure_output_directory(output_dir):
    """
    Ensure the output directory exists.
    
    Args:
        output_dir (str): Path to the output directory
        
    Raises:
        Exception: If directory creation fails
    """
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except Exception as e:
            raise Exception(f'Error creating output directory: {str(e)}') 