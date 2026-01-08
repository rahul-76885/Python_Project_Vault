import requests
import argparse


def download_image(url, output):
    """
    Core logic function.
    
    Downloads an image from the given URL and saves it locally
    with the provided output filename.

    This function:
    - Makes an HTTP GET request
    - Streams data to avoid high memory usage
    - Writes image bytes in binary mode

    IMPORTANT:
    - This function is reusable:
      • Can be called directly
      • Can be used by CLI
      • Can be unit tested
    """

    # Send HTTP request (stream=True avoids loading full file into memory)
    response = requests.get(url, stream=True)

    # Raise exception if status code is not 200 (4xx / 5xx)
    response.raise_for_status()

    # Open file in binary write mode
    with open(output, "wb") as f:
        # Write response data in chunks
        for chunk in response.iter_content(1024):
            f.write(chunk)

    print(f"✅ Image saved as {output}")


def main():
    """
    CLI entry point.

    This function:
    - Defines how users interact via terminal
    - Parses command-line arguments
    - Passes user input to the core logic function

    This function is called by:
    - pip-installed CLI via setup.py entry_points
    """

    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Download an image from the internet"
    )

    # Required argument: image URL
    parser.add_argument(
        "--url",
        required=True,
        help="Direct image URL"
    )

    # Optional argument: output filename
    parser.add_argument(
        "--output",
        default="rahul.png",
        help="Output file name (default: rahul.png)"
    )

    # Parse terminal arguments into Python object
    args = parser.parse_args()

    # Call core logic
    download_image(args.url, args.output)


# -------------------------------------------------
# This block allows INDIVIDUAL execution:
#
# python cli.py
#
# It does NOT run when:
# - File is imported
# - CLI is executed via pip entry_points
# -------------------------------------------------
if __name__ == "__main__":
    # Individual test run (no argparse needed)
    download_image(
        "https://images.unsplash.com/photo-1503023345310-bd7c1de61c7d",
        "rahul.png"
    )
