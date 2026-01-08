import requests
import argparse

def download_image(url, output):
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(output, "wb") as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)

    print(f"✅ Image saved as {output}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--output", default="rahul.png")

    args = parser.parse_args()
    download_image(args.url, args.output)

if __name__ == "__main__":
    # Individual test run
    download_image(
        "https://images.unsplash.com/photo-1503023345310-bd7c1de61c7d",
        "rahul.png"
    )